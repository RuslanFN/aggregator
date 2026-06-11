from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload 
from models import Event, Place, Sync
from datetime import datetime
from typing import List
from uuid import UUID

class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def get_event_stmt(self):
        stmt = (
            select(Event)
            .order_by(Event.changed_at.desc())
            .options(joinedload(Event.place))
            )
        return stmt
    
    async def get_events(self) -> List[Event]:
        stmt = self.get_event_stmt()
        events = await self.session.execute(stmt)
        return events.scalars().all()
    
    async def get_event_later_than(self, changed_at: datetime) -> List[Event]:
        stmt = self.get_event_stmt().where(Event.changed_at > changed_at)
        events_query = await self.session.execute(stmt)
        return events_query.scalars().all()

    async def get_event_by_id(self, event_id: int) -> Event:
        stmt = select(Event).where(Event.id == event_id)
        event_query = await self.session.execute(stmt)
        return event_query.scalar_one_or_none()

    async def create_or_update_event(
        self,
        external_id: UUID,
        external_created_at: datetime,
        external_changed_at: datetime,
        place: Place,
        name: str,
        event_time: datetime,
        registration_deadline: datetime,
        status: str,
        number_of_visitors: int,
        status_changed_at: datetime
        ) -> Event:
        stmt = select(Event).where(Event.external_id == external_id)
        event_query = await self.session.execute(stmt)
        event = event_query.scalar_one_or_none()

        if event:
            event.external_changed_at = external_changed_at
            event.place = place
            event.name = name
            event.event_time = event_time
            event.registration_deadline = registration_deadline
            event.status = status
            event.number_of_visitors = number_of_visitors
            event.status_changed_at = status_changed_at
            return event
        event = Event(
            external_id=external_id,
            external_created_at=external_created_at,
            external_changed_at=external_changed_at,
            place=place,
            name=name,
            event_time=event_time,
            registration_deadline=registration_deadline,
            status=status,
            number_of_visitors=number_of_visitors,
            status_changed_at=status_changed_at)
        self.session.add(event)
        return event

class PlaceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_place_by_id(self, place_id: int) -> Place:
        stmt = select(Place).where(Place.id == place_id)
        place_query = await self.session.execute(stmt)
        return place_query.scalar_one_or_none()

    async def get_or_create_place(
        self,
        external_id: UUID,
        name: str,
        city: str,
        adress: str,
        seats_pattern: str) -> Place:
        stmt = select(Place).where(Place.external_id == external_id)
        place_query = await self.session.execute(stmt)
        place = place_query.scalar_one_or_none()
        if place:
            return place
        place = Place(
            external_id = external_id,
            name = name,
            city = city,
            adress = adress,
            seats_pattern = seats_pattern
            )
        self.session.add(place)
        return place

class SyncRepository:
    def __init__(self, session: Session):
        self.session = session

    async def get_last_sync_or_none(self):
        stmt = select(Sync).order_by(desc(Sync.changed_at)).limit(1)
        last_synce = await self.session.execute(stmt)
        return last_synce.scalar_one_or_none()

    
