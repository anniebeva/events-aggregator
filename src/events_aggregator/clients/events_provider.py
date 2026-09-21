import httpx

from events_aggregator.clients.exceptions import ProviderError, ProviderNotFoundError


class EventsProviderClient:
    """Provide access to the external Events Provider API"""

    def __init__(self, base_url: str, api_key: str):
        """Initialize the HTTP client with Provider settings"""
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={'x-api-key': api_key},
        )

    def _handle_response(self, response: httpx.Response):
        """Handle an Events Provider response"""
        if response.status_code == 404:
            raise ProviderNotFoundError

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise ProviderError from error

        return response

    async def events(self, changed_at: str):
        """Get events changed after the specified date"""
        response = await self.client.get(
            '/api/events/',
            params={'changed_at': changed_at},
        )
        self._handle_response(response)
        return response.json()

    async def events_page(self, url: str):
        """Get an events page using the Provider pagination URL"""
        response = await self.client.get(url)
        self._handle_response(response)
        return response.json()

    async def seats(self, event_id: str):
        """Get available seats for an event"""
        response = await self.client.get(
            f'/api/events/{event_id}/seats/',
        )
        self._handle_response(response)
        return response.json()

    async def register(
        self,
        event_id: str,
        first_name: str,
        last_name: str,
        seat: str,
        email: str,
    ):
        """Register a participant for an event"""
        response = await self.client.post(
            f'/api/events/{event_id}/register/',
            json={
                'first_name': first_name,
                'last_name': last_name,
                'seat': seat,
                'email': email,
            },
        )
        self._handle_response(response)
        return response.json()

    async def unregister(self, event_id: str, ticket_id: str):
        """Cancel an event registration"""
        response = await self.client.delete(
            f'/api/events/{event_id}/unregister/',
            json={'ticket_id': ticket_id},
        )
        self._handle_response(response)
        return response.json()

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
