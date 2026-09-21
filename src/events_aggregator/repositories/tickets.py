from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.models.ticket import Ticket


class TicketRepository:
    """Provide database operations for tickets"""

    def __init__(self, session: AsyncSession):
        """Initialize the repository with its database session"""
        self.session = session

    async def get(self, ticket_id: UUID):
        """Get a ticket by ID"""
        result = await self.session.execute(
            select(Ticket).where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def create(self, ticket: Ticket):
        """Add a new ticket to the database"""
        self.session.add(ticket)
        await self.session.flush()
