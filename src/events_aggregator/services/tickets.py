from uuid import UUID, uuid4

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.models.registration import Registration
from events_aggregator.models.ticket import Ticket
from events_aggregator.repositories.registrations import RegistrationRepository
from events_aggregator.repositories.tickets import TicketRepository
from events_aggregator.services.exceptions import SeatNotAvailableError


class TicketService:
    """Handle ticket registration and cancellation"""

    def __init__(
        self,
        client: EventsProviderClient,
        ticket_repository: TicketRepository,
        registration_repository: RegistrationRepository,
    ):
        """Initialize the ticket service with its dependencies"""
        self.client = client
        self.ticket_repository = ticket_repository
        self.registration_repository = registration_repository

    async def create(
        self,
        event_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ):
        """Register a participant and save the ticket"""
        available_seats = await self.client.seats(str(event_id))

        if seat not in available_seats["seats"]:
            raise SeatNotAvailableError

        result = await self.client.register(
            str(event_id),
            first_name,
            last_name,
            seat,
            email,
        )

        ticket_id = UUID(result["ticket_id"])

        ticket = await self.ticket_repository.get(ticket_id)

        if ticket is None:
            ticket = Ticket(
                id=ticket_id,
                event_id=event_id,
                seat=seat,
            )
            await self.ticket_repository.create(ticket)

        registration = Registration(
            id=uuid4(),
            ticket_id=ticket_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        await self.registration_repository.create(registration)

        return ticket

    async def delete(self, ticket_id: UUID):
        """Cancel a registration"""
        ticket = await self.ticket_repository.get(ticket_id)

        if ticket is None:
            return None

        await self.client.unregister(
            str(ticket.event_id),
            str(ticket.id),
        )

        registration = await self.registration_repository.get_by_ticket_id(ticket_id)

        if registration:
            await self.registration_repository.delete(registration)

        return ticket
