from sqlalchemy.ext.asyncio import AsyncSession
from repository import EventRepository, PlaceRepository, SyncRepository
from API_utils import get_all_events
from schemas import EventApiResponse, EventResponse
from models import SyncMetaData
from aiohttp import ClientSession
from datetime import datetime
from typing import List
from config import get_logger, get_base_url

logger = get_logger(__name__)

class EventService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def sync_events(self, client: ClientSession):
        event_repository = EventRepository(self.session)
        place_repository = PlaceRepository(self.session)
        sync_repository = SyncRepository(self.session)
        sync = SyncMetaData(sync_status='started')
        last_sync: SyncMetaData = await sync_repository.get_last_sync_or_none()
        try:
            if last_sync:
                last_changed = last_sync.last_changed_at.strftime("%Y-%m-%d")
                events: List[EventApiResponse] = await get_all_events(client, date_from=last_changed)
            else:
                events: List[EventApiResponse] = await get_all_events(client)
            if events:
                last_changed_event = max(events, key=lambda x: x.changed_at)
                last_changed_at = last_changed_event.changed_at
                sync.last_changed_at = last_changed_at
            elif last_sync:
                sync.last_changed_at = last_sync.last_changed_at
            for event in events:
                place = await place_repository.get_or_create_place(
                    external_id=event.place.id,
                    name=event.place.name,
                    city=event.place.city,
                    address=event.place.address,
                    seats_pattern=event.place.seats_pattern,
                )
                new_event = await event_repository.create_or_update_event(
                    external_id=event.id,
                    external_changed_at=event.changed_at,
                    external_created_at=event.created_at,
                    place=place,
                    name=event.name,
                    event_time=event.event_time,
                    registration_deadline=event.registration_deadline,
                    status=event.status,
                    number_of_visitors=event.number_of_visitors,
                    status_changed_at=event.status_changed_at)
            sync.sync_status = 'complite'
            self.session.add(sync)
            await self.session.commit()
            logger.info('Синхронизация данных')
        except Exception as e:
            logger.error(f'Ошибка синхронизации {e}')
            raise Exception(f'Ошибка синехронизации')
    
    async def get_events_later_than(
        self,
        host_name: str, 
        date_from: datetime=datetime.strptime('2000-01-01', "%Y-%m-%d"),
        page: int=1,
        page_size: int=20) -> List[EventResponse]:
        event_repository = EventRepository(self.session)
        events = await event_repository.get_event_later_than(
            date_from,
            page,
            page_size)
        count = await event_repository.get_count_event(date_from)
        page_count = count // page_size
        if page < page_count:
            next_page = f'{host_name}/api/events/?page={page+1}&page_size={page_size}&date_from={date_from}'
        else:
            next_page = None
        if page > 1:
            previus_page = f'{host_name}/api/events/?page={page-1}&page_size={page_size}&date_from={date_from}'
        else:
            previus_page = None
        
        result = {
            'count': count,
            'next': next_page,
            'previous': previus_page,
            'results': events}
        return result
        
        


