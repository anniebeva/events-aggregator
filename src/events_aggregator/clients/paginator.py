from events_aggregator.clients.events_provider import EventsProviderClient


class EventsPaginator:
    """Iterate through all event pages from the Events Provider"""

    def __init__(self, client: EventsProviderClient, changed_at: str):
        """Initialize the paginator with Provider client and sync date"""
        self.client = client
        self.changed_at = changed_at

    async def __aiter__(self):
        """Yield events from all Provider pages"""
        page = await self.client.events(self.changed_at)

        while page:
            for event in page["results"]:
                yield event

            if not page["next"]:
                break

            page = await self.client.events_page(page["next"])
