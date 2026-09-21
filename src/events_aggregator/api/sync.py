from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.core.config import settings
from events_aggregator.core.database import get_session
from events_aggregator.repositories.events import EventRepository
from events_aggregator.repositories.places import PlaceRepository
from events_aggregator.repositories.sync_metadata import SyncMetadataRepository
from events_aggregator.services.sync import SyncService

router = APIRouter()


def get_sync_service(
    session: AsyncSession = Depends(get_session),
) -> SyncService:
    """Create a sync service with its dependencies"""
    client = EventsProviderClient(
        settings.events_provider_url,
        settings.events_provider_api_key,
    )

    return SyncService(
        client=client,
        event_repository=EventRepository(session),
        place_repository=PlaceRepository(session),
        metadata_repository=SyncMetadataRepository(session),
    )


@router.post("/api/sync/trigger", status_code=200)
async def trigger_sync(
    service: SyncService = Depends(get_sync_service),
):
    """Trigger events synchronization"""
    await service.sync()

    return {"status": "ok"}
