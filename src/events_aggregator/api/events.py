import time
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.core.config import settings
from events_aggregator.core.database import get_session
from events_aggregator.repositories.events import EventRepository

router = APIRouter()

seats_cache = {}


def get_event_repository(
    session: AsyncSession = Depends(get_session),
) -> EventRepository:
    """Create an event repository with its database session"""
    return EventRepository(session)


def get_events_provider_client() -> EventsProviderClient:
    """Create an Events Provider client"""
    if not settings.events_provider_url:
        raise RuntimeError('Events Provider URL is not configured')

    if not settings.events_provider_api_key:
        raise RuntimeError('Events Provider API key is not configured')

    return EventsProviderClient(
        settings.events_provider_url,
        settings.events_provider_api_key,
    )

@router.get('/api/events')
async def get_events(
    request: Request,
    date_from: datetime | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1),
    repository: EventRepository = Depends(get_event_repository),
):
    """Return a paginated list of events"""
    events, count = await repository.get_list(
        date_from=date_from,
        page=page,
        page_size=page_size,
    )

    results = [
        {
            'id': event.id,
            'name': event.name,
            'place': {
                'id': place.id,
                'name': place.name,
                'city': place.city,
                'address': place.address,
            },
            'event_time': event.event_time,
            'registration_deadline': event.registration_deadline,
            'status': event.status,
            'number_of_visitors': event.number_of_visitors,
            'changed_at': event.changed_at,
            'created_at': event.created_at,
            'status_changed_at': event.status_changed_at,
        }
        for event, place in events
    ]

    def build_url(page_number: int):
        """Build a pagination URL for the requested page"""
        params = {
            'page': page_number,
            'page_size': page_size,
        }

        if date_from:
            params['date_from'] = date_from.isoformat()

        return str(request.url.replace_query_params(**params))

    next_url = None

    if page * page_size < count:
        next_url = build_url(page + 1)

    previous_url = None

    if page > 1:
        previous_url = build_url(page - 1)

    return {
        'count': count,
        'next': next_url,
        'previous': previous_url,
        'results': results,
    }

@router.get('/api/events/{event_id}')
async def get_event(
    event_id: UUID,
    repository: EventRepository = Depends(get_event_repository),
):
    """Return an event by its ID"""
    result = await repository.get(event_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail='Event not found',
        )

    event, place = result

    return {
        'id': event.id,
        'name': event.name,
        'place': {
            'id': place.id,
            'name': place.name,
            'city': place.city,
            'address': place.address,
        },
        'event_time': event.event_time,
        'registration_deadline': event.registration_deadline,
        'status': event.status,
        'number_of_visitors': event.number_of_visitors,
        'changed_at': event.changed_at,
        'created_at': event.created_at,
        'status_changed_at': event.status_changed_at,
    }

@router.get('/api/events/{event_id}/seats')
async def get_event_seats(
    event_id: UUID,
    client: EventsProviderClient = Depends(get_events_provider_client),
):
    """Return available seats for an event"""
    cache_key = str(event_id)
    cached = seats_cache.get(cache_key)

    if cached:
        cached_at, seats = cached

        if time.monotonic() - cached_at < 30:
            return seats

    seats = await client.seats(cache_key)

    seats_cache[cache_key] = (
        time.monotonic(),
        seats,
    )

    return seats
