from uuid import UUID

from pydantic import BaseModel, EmailStr


class TicketCreate(BaseModel):
    event_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    seat: str


class TicketResponse(BaseModel):
    ticket_id: UUID
