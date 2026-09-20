from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PlaceResponse(BaseModel):
    """Represent a place in an API response"""

    id: UUID
    name: str
    city: str
    address: str


class EventResponse(BaseModel):
    """Represent an event in an API response"""

    id: UUID
    name: str
    place: PlaceResponse
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int
    changed_at: datetime
    created_at: datetime
    status_changed_at: datetime
