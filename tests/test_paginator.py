import asyncio
from unittest.mock import AsyncMock

from events_aggregator.clients.paginator import EventsPaginator


def test_paginator_returns_all_events():
    """Return events from all Provider pages"""

    async def run_test():
        client = AsyncMock()

        client.events.return_value = {
            "results": [
                {"id": "event-1"},
                {"id": "event-2"},
            ],
            "next": "http://provider/api/events/?cursor=next",
        }

        client.events_page.return_value = {
            "results": [
                {"id": "event-3"},
            ],
            "next": None,
        }

        paginator = EventsPaginator(
            client,
            "2000-01-01",
        )

        events = []

        async for event in paginator:
            events.append(event)

        assert events == [
            {"id": "event-1"},
            {"id": "event-2"},
            {"id": "event-3"},
        ]

        client.events.assert_awaited_once_with("2000-01-01")
        client.events_page.assert_awaited_once_with(
            "http://provider/api/events/?cursor=next",
        )

    asyncio.run(run_test())


def test_paginator_stops_on_last_page():
    """Stop pagination when there is no next page"""

    async def run_test():
        client = AsyncMock()

        client.events.return_value = {
            "results": [
                {"id": "event-1"},
            ],
            "next": None,
        }

        paginator = EventsPaginator(
            client,
            "2000-01-01",
        )

        events = []

        async for event in paginator:
            events.append(event)

        assert events == [
            {"id": "event-1"},
        ]

        client.events.assert_awaited_once_with("2000-01-01")
        client.events_page.assert_not_awaited()

    asyncio.run(run_test())
