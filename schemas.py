from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import List
class GetEventsParams(BaseModel):
    date_from: str | None = Field(
        default=None, 
        description='YYYY-MM-DD')
    page: int = Field(default=1) 
    page_size: int = Field(default=20)

    @field_validator('date_from')
    @classmethod
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Incorrect date format, should be YYYY-MM-DD')

class PlaceApiResponse(BaseModel):
    id: UUID
    name: str
    city: str
    adress: str
    seats_pattern: str
    changed_at: datetime
    created_at: datetime

class EventApiResponse(BaseModel):
    id: UUID
    name: str
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int
    place: PlaceApiResponse
    changed_at: datetime
    created_at: datetime
    status_changed_at: datetime

class EventsApiResponse(BaseModel):
    next: str | None = Field(default=None)
    previous: str | None = Field(default=None)
    results: List[EventApiResponse]