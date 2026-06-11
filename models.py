from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, Relationship
from sqlalchemy import func, ForeignKey, DateTime
from datetime import datetime
import uuid


class Base(DeclarativeBase):
    """
    Base class for all models
    Conteins service fields
    """
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now())
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now())

class Place(Base):
    """class for Places"""
    __tablename__ = 'places'
    external_id: Mapped[int] = mapped_column()
    name: Mapped[str] = mapped_column(unique=True)
    city: Mapped[str] = mapped_column()
    adress: Mapped[str] = mapped_column()
    seats_pattern: Mapped[int] = mapped_column()

class Event(Base):
    """class for Events"""
    __tablename__ = 'events'
    external_id: Mapped[uuid.UUID] = mapped_column()
    external_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    external_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    place_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(Place.id))
    name: Mapped[str] = mapped_column(unique=True)
    event_date: Mapped[datetime] = mapped_column()
    registration_deadline: Mapped[datetime] = mapped_column()
    status: Mapped[str] = mapped_column()
    number_of_visitors: Mapped[int] = mapped_column()
    status_changed_at: Mapped[datetime] = mapped_column()
    place: Mapped[Place] = Relationship(back_populates='events')    

class SyncMetaData(Base):
    """class for SyncInfo"""
    __tablename__ = 'sync_meta_data'
    last_sync_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sync_status: Mapped[str] = mapped_column()

    