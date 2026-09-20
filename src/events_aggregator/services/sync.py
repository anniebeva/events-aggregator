from datetime import UTC, datetime
from uuid import UUID

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.clients.paginator import EventsPaginator
from events_aggregator.models.event import Event
from events_aggregator.models.place import Place
from events_aggregator.models.sync_metadata import SyncMetadata
from events_aggregator.repositories.events import EventRepository
from events_aggregator.repositories.places import PlaceRepository
from events_aggregator.repositories.sync_metadata import SyncMetadataRepository


class SyncService:
    """Synchronize events and places from the Provider to the local database"""

    def __init__(
        self,
        client: EventsProviderClient,
        event_repository: EventRepository,
        place_repository: PlaceRepository,
        metadata_repository: SyncMetadataRepository,
    ):
        """Initialize the sync service with its dependencies"""
        self.client = client
        self.event_repository = event_repository
        self.place_repository = place_repository
        self.metadata_repository = metadata_repository

    async def sync(self):
        """Synchronize all changed events from the Provider"""
        metadata = await self.metadata_repository.get()

        if metadata is None:
            metadata = SyncMetadata(
                id=1,
                sync_status='running',
            )
            await self.metadata_repository.create(metadata)

        else:
            metadata.sync_status = 'running'
            await self.metadata_repository.update(metadata)

        changed_at = '2000-01-01'

        if metadata.last_changed_at is not None:
            changed_at = metadata.last_changed_at.date().isoformat()

        paginator = EventsPaginator(
            self.client,
            changed_at,
        )

        last_changed_at = None

        try:
            async for event_data in paginator:
                place = await self._sync_place(event_data['place'])

                event = await self.event_repository.get_event(
                    UUID(event_data['id'])
                )

                if event:
                    self._update_event(event, event_data)
                else:
                    event = self._create_event(event_data, place)
                    await self.event_repository.create(event)

                event_changed_at = datetime.fromisoformat(
                    event_data['changed_at']
                )

                if (
                    last_changed_at is None
                    or event_changed_at > last_changed_at
                ):
                    last_changed_at = event_changed_at

            metadata.last_sync_time = datetime.now(UTC)

            if last_changed_at is not None:
                metadata.last_changed_at = last_changed_at

            metadata.sync_status = 'success'

            await self.metadata_repository.update(metadata)

        except Exception:
            metadata.last_sync_time = datetime.now(UTC)
            metadata.sync_status = 'failed'

            await self.metadata_repository.update(metadata)

            raise

    async def _sync_place(self, place_data: dict) -> Place:
        """Create or update a place from Provider data"""
        place_id = UUID(place_data['id'])

        place = await self.place_repository.get(place_id)

        if place:
            place.name = place_data['name']
            place.city = place_data['city']
            place.address = place_data['address']
            place.seats_pattern = place_data['seats_pattern']
            place.changed_at = datetime.fromisoformat(
                place_data['changed_at']
            )
            place.created_at = datetime.fromisoformat(
                place_data['created_at']
            )

            await self.place_repository.update(place)

            return place

        place = Place(
            id=place_id,
            name=place_data['name'],
            city=place_data['city'],
            address=place_data['address'],
            seats_pattern=place_data['seats_pattern'],
            changed_at=datetime.fromisoformat(
                place_data['changed_at']
            ),
            created_at=datetime.fromisoformat(
                place_data['created_at']
            ),
        )

        await self.place_repository.create(place)

        return place

    def _create_event(
        self,
        event_data: dict,
        place: Place,
    ) -> Event:
        """Create an Event model from Provider data"""
        return Event(
            id=UUID(event_data['id']),
            name=event_data['name'],
            event_time=datetime.fromisoformat(
                event_data['event_time']
            ),
            registration_deadline=datetime.fromisoformat(
                event_data['registration_deadline']
            ),
            status=event_data['status'],
            number_of_visitors=event_data['number_of_visitors'],
            changed_at=datetime.fromisoformat(
                event_data['changed_at']
            ),
            created_at=datetime.fromisoformat(
                event_data['created_at']
            ),
            status_changed_at=datetime.fromisoformat(
                event_data['status_changed_at']
            ),
            place_id=place.id,
        )

    def _update_event(
        self,
        event: Event,
        event_data: dict,
    ):
        """Update an existing Event model with Provider data"""
        event.name = event_data['name']
        event.event_time = datetime.fromisoformat(
            event_data['event_time']
        )
        event.registration_deadline = datetime.fromisoformat(
            event_data['registration_deadline']
        )
        event.status = event_data['status']
        event.number_of_visitors = event_data['number_of_visitors']
        event.changed_at = datetime.fromisoformat(
            event_data['changed_at']
        )
        event.status_changed_at = datetime.fromisoformat(
            event_data['status_changed_at']
        )
