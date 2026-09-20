from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.models.place import Place


class PlaceRepository:
    """Provide database operations for places"""

    def __init__(self, session: AsyncSession):
        """Initialize the repository with a database session"""
        self.session = session

    async def get(self, place_id: UUID):
        """Get a place by its ID"""
        result = await self.session.execute(
            select(Place).where(Place.id == place_id)
        )
        return result.scalar_one_or_none()

    async def create(self, place: Place):
        """Add a new place to the database"""
        self.session.add(place)
        await self.session.flush()

    async def update(self, place: Place):
        """Update an existing place in the database"""
        self.session.add(place)
        await self.session.flush()
