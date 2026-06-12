from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload 
from models import Event, Place, SyncMetaData
from datetime import datetime
from typing import List
from uuid import UUID
from dotenv import load_dotenv
import os
load_dotenv()


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def get_event_stmt(self):
        stmt = (
            select(Event)
            .order_by(Event.external_changed_at.desc())
            .options(joinedload(Event.place))
            )
        return stmt
    def get_event_stmt_by_page(
            self, 
            date_from: datetime,
            page: int,
            page_size: int):
        offset = (page - 1) * page_size
        stmt = (
            self.get_event_stmt()
            .where(Event.external_changed_at > date_from)
            .offset(offset)
            .limit(page_size))
        return stmt
    
    async def get_events(self) -> List[Event]:
        stmt = self.get_event_stmt()
        events = await self.session.execute(stmt)
        return events.scalars().all()
    
    async def get_count_event(self, date_from: datetime):
        stmt = (select(func.count()).select_from(Event)
                .where(Event.external_changed_at > date_from))
        count_query = await self.session.execute(stmt)
        count = count_query.scalar_one()
        return count

    async def get_event_later_than(
        self, 
        changed_at: datetime,
        page: int = 1,
        page_size: int = 20) -> List[Event]:
        stmt = self.get_event_stmt_by_page(changed_at, page, page_size)
        events_query = await self.session.execute(stmt)
        events = events_query.scalars().all()
        return events

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
        address: str,
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
            address = address,
            seats_pattern = seats_pattern
            )
        self.session.add(place)
        return place

class SyncRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_last_sync_or_none(self):
        stmt = select(SyncMetaData).order_by(desc(SyncMetaData.changed_at)).limit(1)
        last_synce = await self.session.execute(stmt)
        return last_synce.scalar_one_or_none()

    
