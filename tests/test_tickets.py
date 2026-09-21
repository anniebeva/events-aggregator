import asyncio
from uuid import UUID

import pytest

from events_aggregator.services.exceptions import SeatNotAvailableError

EVENT_ID = UUID("d2da8e51-8470-4bf2-a95a-f712582e2f64")
TICKET_ID = UUID("d2da8e51-8470-4bf2-a95a-f712582e2f64")
PLACE_ID = UUID("b3a1c1e4-1c2d-4f2b-8e6d-9b8f3a3c4d5e")


def test_create_ticket(client, mock_ticket_service):
    """Create a ticket"""
    ticket = type("Ticket", (), {"id": TICKET_ID})()

    mock_ticket_service.create.return_value = ticket

    response = client.post(
        "/api/tickets",
        json={
            "event_id": str(EVENT_ID),
            "first_name": "Иван",
            "last_name": "Иванов",
            "email": "ivan@example.com",
            "seat": "A15",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "ticket_id": str(TICKET_ID),
    }

    mock_ticket_service.create.assert_awaited_once_with(
        event_id=EVENT_ID,
        first_name="Иван",
        last_name="Иванов",
        email="ivan@example.com",
        seat="A15",
    )


def test_delete_ticket(client, mock_ticket_service):
    """Cancel a ticket"""
    mock_ticket_service.delete.return_value = object()

    response = client.delete(f"/api/tickets/{TICKET_ID}")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
    }

    mock_ticket_service.delete.assert_awaited_once_with(TICKET_ID)


def test_delete_ticket_not_found(client, mock_ticket_service):
    """Return 404 when ticket does not exist"""
    mock_ticket_service.delete.return_value = None

    response = client.delete(f"/api/tickets/{TICKET_ID}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Ticket not found",
    }

    mock_ticket_service.delete.assert_awaited_once_with(TICKET_ID)


def test_create_ticket_service(ticket_service):
    """Create a ticket and registration"""
    service, provider_client, ticket_repository, registration_repository = (
        ticket_service
    )

    provider_client.seats.return_value = {
        "seats": ["A15"],
    }

    provider_client.register.return_value = {
        "ticket_id": str(TICKET_ID),
    }

    ticket_repository.get.return_value = None

    ticket = asyncio.run(
        service.create(
            event_id=PLACE_ID,
            first_name="Иван",
            last_name="Иванов",
            email="ivan@example.com",
            seat="A15",
        )
    )

    assert ticket.id == TICKET_ID

    provider_client.register.assert_awaited_once()
    ticket_repository.get.assert_awaited_once_with(TICKET_ID)
    ticket_repository.create.assert_awaited_once()
    registration_repository.create.assert_awaited_once()


def test_create_ticket_unavailable_seat(ticket_service):
    """Reject an unavailable seat"""
    service, provider_client, _, _ = ticket_service

    provider_client.seats.return_value = {
        "seats": ["A7", "D10", "B13"],
    }

    with pytest.raises(SeatNotAvailableError):
        asyncio.run(
            service.create(
                event_id=PLACE_ID,
                first_name="Иван",
                last_name="Иванов",
                email="ivan@example.com",
                seat="A15",
            )
        )

    provider_client.register.assert_not_awaited()
