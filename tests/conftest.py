from types import SimpleNamespace

import pytest


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
