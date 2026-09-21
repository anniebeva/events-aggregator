from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from events_aggregator.api.events import (
    get_event_repository,
    get_events_provider_client,
    seats_cache,
)
from events_aggregator.clients.exceptions import ProviderNotFoundError
from events_aggregator.main import app

client = TestClient(app)


def test_get_events(event, place):
    """Return paginated events"""
    repository = AsyncMock()
    repository.get_list.return_value = (
        [(event, place)],
        1,
    )

    app.dependency_overrides[get_event_repository] = lambda: repository

    response = client.get("/api/events")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert data["next"] is None
    assert data["previous"] is None
    assert len(data["results"]) == 1
    assert data["results"][0]["name"] == event.name
    assert data["results"][0]["place"]["city"] == place.city

    repository.get_list.assert_awaited_once_with(
        date_from=None,
        page=1,
        page_size=20,
    )

    app.dependency_overrides.clear()


def test_get_events_pagination(event, place):
    """Return the next and previous page URLs"""
    repository = AsyncMock()
    repository.get_list.return_value = (
        [(event, place)],
        41,
    )

    app.dependency_overrides[get_event_repository] = lambda: repository

    response = client.get(
        "/api/events?page=2&page_size=20",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 41
    assert data["next"] is not None
    assert "page=3" in data["next"]
    assert "page_size=20" in data["next"]
    assert data["previous"] is not None
    assert "page=1" in data["previous"]

    repository.get_list.assert_awaited_once_with(
        date_from=None,
        page=2,
        page_size=20,
    )

    app.dependency_overrides.clear()


def test_get_event(event, place):
    """Return an event by ID"""
    repository = AsyncMock()
    repository.get.return_value = (event, place)

    app.dependency_overrides[get_event_repository] = lambda: repository

    response = client.get(f"/api/events/{event.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == event.id
    assert data["name"] == event.name
    assert data["place"]["name"] == place.name
    assert data["place"]["city"] == place.city
    assert data["place"]["address"] == place.address
    assert data["place"]["seats_pattern"] == place.seats_pattern

    repository.get.assert_awaited_once()

    app.dependency_overrides.clear()


def test_get_event_not_found():
    """Return 404 when an event does not exist"""
    repository = AsyncMock()
    repository.get.return_value = None

    app.dependency_overrides[get_event_repository] = lambda: repository

    event_id = "d2da8e51-8470-4bf2-a95a-f712582e2f64"

    response = client.get(f"/api/events/{event_id}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Event not found",
    }

    repository.get.assert_awaited_once()

    app.dependency_overrides.clear()


def test_get_event_seats():
    """Return available seats from the Provider"""
    seats_cache.clear()

    provider = AsyncMock()
    provider.seats.return_value = {
        "seats": ["A1", "A2", "B1"],
    }

    app.dependency_overrides[get_events_provider_client] = lambda: provider

    event_id = "d2da8e51-8470-4bf2-a95a-f712582e2f64"

    response = client.get(
        f"/api/events/{event_id}/seats",
    )

    assert response.status_code == 200

    assert response.json() == {
        "event_id": event_id,
        "available_seats": ["A1", "A2", "B1"],
    }

    provider.seats.assert_awaited_once_with(event_id)

    app.dependency_overrides.clear()
    seats_cache.clear()


def test_get_event_seats_uses_cache():
    """Return cached seats without calling the Provider again"""
    seats_cache.clear()

    provider = AsyncMock()
    provider.seats.return_value = {
        "seats": ["A1", "A2"],
    }

    app.dependency_overrides[get_events_provider_client] = lambda: provider

    event_id = "d2da8e51-8470-4bf2-a95a-f712582e2f64"
    url = f"/api/events/{event_id}/seats"

    first_response = client.get(url)
    second_response = client.get(url)

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json() == second_response.json()

    provider.seats.assert_awaited_once_with(event_id)

    app.dependency_overrides.clear()
    seats_cache.clear()


def test_get_event_seats_not_found():
    """Return 404 when the Provider cannot find the event"""
    seats_cache.clear()

    provider = AsyncMock()
    provider.seats.side_effect = ProviderNotFoundError

    app.dependency_overrides[get_events_provider_client] = lambda: provider

    event_id = "d2da8e51-8470-4bf2-a95a-f712582e2f64"

    response = client.get(
        f"/api/events/{event_id}/seats",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Event not found",
    }

    provider.seats.assert_awaited_once_with(event_id)

    app.dependency_overrides.clear()
    seats_cache.clear()
