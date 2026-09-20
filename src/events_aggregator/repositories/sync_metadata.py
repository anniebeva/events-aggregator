from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.models.sync_metadata import SyncMetadata


class SyncMetadataRepository:
    """Provide database operations for synchronization metadata"""

    def __init__(self, session: AsyncSession):
        """Initialize the repository with a database session"""
        self.session = session

    async def get(self):
        """Get synchronization metadata"""
        result = await self.session.execute(
            select(SyncMetadata).where(SyncMetadata.id == 1)
        )
        return result.scalar_one_or_none()

    async def create(self, metadata: SyncMetadata):
        """Add synchronization metadata to the database"""
        self.session.add(metadata)
        await self.session.flush()

    async def update(self, metadata: SyncMetadata):
        """Update synchronization metadata in the database"""
        self.session.add(metadata)
        await self.session.flush()
