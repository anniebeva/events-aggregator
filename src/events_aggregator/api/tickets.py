from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.core.config import settings
from events_aggregator.core.database import get_session
from events_aggregator.repositories.registrations import RegistrationRepository
from events_aggregator.repositories.tickets import TicketRepository
from events_aggregator.schemas.tickets import TicketCreate, TicketResponse
from events_aggregator.services.exceptions import SeatNotAvailableError
from events_aggregator.services.tickets import TicketService

router = APIRouter()


def get_ticket_repository(
    session: AsyncSession = Depends(get_session),
) -> TicketRepository:
    """Create a ticket repository with its database session"""
    return TicketRepository(session)


def get_registration_repository(
    session: AsyncSession = Depends(get_session),
) -> RegistrationRepository:
    """Create a registration repository with its database session"""
    return RegistrationRepository(session)


def get_events_provider_client() -> EventsProviderClient:
    """Create an Events Provider client"""
    return EventsProviderClient(
        settings.events_provider_url,
        settings.events_provider_api_key,
    )


def get_ticket_service(
    client: EventsProviderClient = Depends(get_events_provider_client),
    ticket_repository: TicketRepository = Depends(get_ticket_repository),
    registration_repository: RegistrationRepository = Depends(
        get_registration_repository,
    ),
) -> TicketService:
    """Create a ticket service with its dependencies"""
    return TicketService(
        client=client,
        ticket_repository=ticket_repository,
        registration_repository=registration_repository,
    )


@router.post("/api/tickets", response_model=TicketResponse, status_code=201)
async def create_ticket(
    data: TicketCreate,
    service: TicketService = Depends(get_ticket_service),
):
    """Register a participant for an event"""
    try:
        ticket = await service.create(
            event_id=data.event_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            seat=data.seat,
        )
    except SeatNotAvailableError:
        raise HTTPException(
            status_code=400,
            detail="Seat is not available",
        )

    return TicketResponse(ticket_id=ticket.id)


@router.delete("/api/tickets/{ticket_id}")
async def delete_ticket(
    ticket_id: UUID,
    service: TicketService = Depends(get_ticket_service),
):
    """Cancel a registration"""
    ticket = await service.delete(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return {"success": True}
