from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from events_aggregator.api.tickets import get_ticket_service
from events_aggregator.main import app
from events_aggregator.services.tickets import TicketService


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def mock_ticket_service():
    """Create a mocked ticket service"""
    service = AsyncMock()

    app.dependency_overrides[get_ticket_service] = lambda: service

    yield service

    app.dependency_overrides.clear()


@pytest.fixture
def ticket_service():
    """Create a ticket service with mocked dependencies"""
    provider_client = AsyncMock()
    ticket_repository = AsyncMock()
    registration_repository = AsyncMock()

    service = TicketService(
        client=provider_client,
        ticket_repository=ticket_repository,
        registration_repository=registration_repository,
    )

    return (
        service,
        provider_client,
        ticket_repository,
        registration_repository,
    )


@pytest.fixture
def event():
    """Create a test event"""
    return SimpleNamespace(
        id="d2da8e51-8470-4bf2-a95a-f712582e2f64",
        name="Test event",
        event_time="2026-09-21T15:00:00+03:00",
        registration_deadline="2026-09-20T15:00:00+03:00",
        status="published",
        number_of_visitors=10,
    )


@pytest.fixture
def place():
    """Create a test place"""
    return SimpleNamespace(
        id="b3a1c1e4-1c2d-4f2b-8e6d-9b8f3a3c4d5e",
        name="Test place",
        city="Moscow",
        address="Test address",
        seats_pattern="A1-20,B1-30",
    )
