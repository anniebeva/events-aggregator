from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.models.registration import Registration


class RegistrationRepository:
    """Provide database operations for registrations"""

    def __init__(self, session: AsyncSession):
        """Initialize the repository with its database session"""
        self.session = session

    async def get_by_ticket_id(self, ticket_id: UUID):
        """Get a registration by ticket ID"""
        result = await self.session.execute(
            select(Registration).where(Registration.ticket_id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def create(self, registration: Registration):
        """Add a new registration to the database"""
        self.session.add(registration)
        await self.session.flush()

    async def delete(self, registration: Registration):
        """Delete a registration from the database"""
        await self.session.delete(registration)
        await self.session.flush()
