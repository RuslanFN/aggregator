from sqlalchemy import AsyncSession
from repository import EventRepository, PlaceRepository, SyncRepository
from API_utils import get_all_events
from schemas import EventsApiResponse
from models import SyncMetaData
from aiohttp import ClientSession
from database import get_session
class EventService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def sync_events(self):
        event_repository = EventRepository(self.session)
        place_repository = PlaceRepository(self.session)
        sync_repository = SyncRepository(self.session)
        
        last_sync: SyncMetaData = await sync_repository.get_last_sync()
        if last_sync:
            last_changed = last_sync.last_changed_at
            events: EventsApiResponse = await get_all_events(date_from=last_changed)
        else:
            events: EventsApiResponse = await get_all_events()

        for event in events.results:
            place = place_repository.get_or_create_place(
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
        await self.session.commit()


