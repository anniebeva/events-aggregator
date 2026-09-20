from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.models.event import Event
from events_aggregator.models.place import Place


class EventRepository:
    """Provide database operations for events"""

    def __init__(self, session: AsyncSession):
        """Initialize the repository with a database session"""
        self.session = session

    async def get(self, event_id: UUID):
        """Get an event with its place by ID"""
        query = select(Event, Place).join(
            Place,
            Event.place_id == Place.id,
        ).where(Event.id == event_id)

        result = await self.session.execute(query)

        return result.one_or_none()

    async def get_list(
            self,
            date_from: datetime | None,
            page: int,
            page_size: int,
    ):
        """Get a paginated list of events"""
        query = select(Event, Place).join(
            Place,
            Event.place_id == Place.id,
        )

        if date_from:
            query = query.where(Event.event_time >= date_from)

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        count = count_result.scalar_one()

        offset = (page - 1) * page_size

        query = query.offset(offset).limit(page_size)

        result = await self.session.execute(query)
        events = result.all()

        return events, count

    async def create(self, event: Event):
        """Add a new event to the database"""
        self.session.add(event)
        await self.session.flush()

    async def update(self, event: Event):
        """Update an existing event in the database"""
        self.session.add(event)
        await self.session.flush()
