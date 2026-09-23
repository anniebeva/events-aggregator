# Events Aggregator

REST API aggregator for events. The application keeps a local copy of events from an external Events Provider, provides local event search and pagination, and handles ticket registration and cancellation through the Provider API.

## Features

* Synchronization of events from the external Events Provider
* Incremental synchronization using `changed_at`
* Local PostgreSQL storage for events and places
* Daily/background synchronization support
* Manual synchronization trigger
* Local event listing with date filtering and pagination
* Event details from the local database
* Current available seats retrieved from the Events Provider
* In-memory seats cache with a 30-second TTL
* Ticket registration through the Events Provider
* Registration cancellation
* Local storage of tickets and registrations
* Provider error handling
* Request validation
* Automated tests
* Docker support
* Database migrations with Alembic
* Code quality checks with Ruff

## Architecture

The application follows a layered architecture:

```text
Client
  │
  ▼
FastAPI API
  │
  ▼
Services
  │
  ├──────────────► Events Provider Client
  │
  ▼
Repositories
  │
  ▼
PostgreSQL
```

The main responsibilities are separated between layers:

* **API**: handles HTTP requests, validation and HTTP responses
* **Services**: contains application and business logic
* **Repositories**: handles database operations
* **Events Provider Client**: contains all communication with the external Events Provider
* **Models**: SQLAlchemy database models
* **Schemas**: Pydantic request and response schemas

The business logic does not depend directly on HTTP or database implementation details.

## Project Structure

```text
src/
└── events_aggregator/
    ├── api/
    │   ├── events.py
    │   ├── sync.py
    │   └── tickets.py
    │
    ├── clients/
    │   ├── events_provider.py
    │   ├── exceptions.py
    │   └── paginator.py
    │
    ├── core/
    │   ├── config.py
    │   └── database.py
    │
    ├── models/
    │   ├── base.py
    │   ├── event.py
    │   ├── place.py
    │   ├── registration.py
    │   ├── sync_metadata.py
    │   └── ticket.py
    │
    ├── repositories/
    │   ├── events.py
    │   ├── places.py
    │   ├── registrations.py
    │   ├── sync_metadata.py
    │   └── tickets.py
    │
    ├── schemas/
    │   └── tickets.py
    │
    ├── services/
    │   ├── exceptions.py
    │   ├── sync.py
    │   └── tickets.py
    │
    └── main.py

tests/
├── conftest.py
├── test_events.py
├── test_paginator.py
└── test_tickets.py

alembic/
└── versions/
```

## Tech Stack

* Python 3.12
* FastAPI
* SQLAlchemy 2.0
* PostgreSQL
* asyncpg
* HTTPX
* Pydantic
* Alembic
* Pytest
* Ruff
* uv
* Docker

## Configuration

Create a `.env` file in the project root:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DATABASE_NAME=events_aggregator

EVENTS_PROVIDER_URL=https://events-provider.dev-2.python-labs.ru
EVENTS_PROVIDER_API_KEY=your_api_key
```

The `.env` file must not be committed to the repository.

## Running Locally

### 1. Install dependencies

The project uses `uv` for dependency management.

```bash
uv sync
```

### 2. Configure environment variables

Create a `.env` file with the required PostgreSQL and Events Provider settings.

### 3. Run database migrations

```bash
uv run alembic upgrade head
```

### 4. Start the application

```bash
uv run uvicorn events_aggregator.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Database Migrations

Alembic is used to manage database schema changes.

Create a new migration:

```bash
uv run alembic revision --autogenerate -m "migration description"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Check the current migration:

```bash
uv run alembic current
```

## Synchronization

Events are synchronized from the external Events Provider into the local PostgreSQL database.

The first synchronization starts from:

```text
2000-01-01
```

After a successful synchronization, the application stores synchronization metadata including:

* `last_sync_time`
* `last_changed_at`
* `sync_status`

Subsequent synchronizations use the stored `last_changed_at` to request only changed events.

Provider pagination is handled by `EventsPaginator`, which follows the Provider's `next` URLs until all pages have been processed.

## API

### Health Check

```http
GET /api/health
```

Returns:

```json
{
  "status": "ok"
}
```

### Trigger Synchronization

```http
POST /api/sync/trigger
```

Triggers an event synchronization.

### List Events

```http
GET /api/events
```

Optional query parameters:

* `date_from` — return events starting from the specified date/time
* `page` — page number, default `1`
* `page_size` — number of events per page, default `20`

Example:

```http
GET /api/events?date_from=2026-09-20T00:00:00&page=1&page_size=20
```

The endpoint reads events from the local PostgreSQL database rather than requesting them from the external Provider.

### Get Event

```http
GET /api/events/{event_id}
```

Returns an event stored in the local database.

### Get Available Seats

```http
GET /api/events/{event_id}/seats
```

Returns currently available seats from the Events Provider.

Seat responses are cached in memory for 30 seconds.

### Register a Ticket

```http
POST /api/tickets
```

Example request:

```json
{
  "event_id": "d2da8e51-8470-4bf2-a95a-f712582e2f64",
  "first_name": "Ivan",
  "last_name": "Ivanov",
  "email": "ivan@example.com",
  "seat": "A15"
}
```

The application:

1. Checks seat availability through the Events Provider
2. Registers the participant with the Provider
3. Stores the ticket locally
4. Stores the current registration locally

Returns:

```json
{
  "ticket_id": "..."
}
```

### Cancel a Ticket

```http
DELETE /api/tickets/{ticket_id}
```

Returns:

```json
{
  "success": true
}
```

When a registration is cancelled, the local `Registration` record is removed while the `Ticket` record is kept.

This allows the same Provider ticket to be associated with a new registration if the seat is registered again later.

## Ticket and Registration Model

Tickets and registrations have different lifecycles.

```text
Event
  │
  └── Ticket
        │
        └── Registration
```

A `Ticket` represents the Provider ticket and its seat for an event.

A `Registration` represents the current participant registered for that ticket.

When a participant cancels:

```text
Ticket        → kept
Registration  → deleted
```

When the same seat is registered again, the existing ticket can be reused and a new registration is created.

## Testing

Run the complete test suite:

```bash
uv run pytest
```

Run a specific test file:

```bash
uv run pytest tests/test_tickets.py
```

The tests cover:

* API endpoints
* request validation
* ticket registration
* ticket cancellation
* unavailable seats
* Provider client interactions
* event pagination
* synchronization-related functionality

External dependencies are mocked in unit tests.

## Code Quality

Ruff is used for linting and code quality checks.

Run Ruff:

```bash
uv run ruff check .
```

The project follows PEP 8 conventions.

## Docker

Build the Docker image:

```bash
docker build -t events-aggregator .
```

Run the application:

```bash
docker run --env-file .env -p 8000:8000 events-aggregator
```

The container applies database migrations before starting the FastAPI application.

## External Events Provider

The application communicates with an external Events Provider API.

All Provider interaction is encapsulated in `EventsProviderClient`.

The client handles:

* event retrieval
* cursor pagination
* available seats
* registration
* registration cancellation
* Provider errors

The API key is passed using the `x-api-key` header and is kept outside the source code.

## Development

Install dependencies including development tools:

```bash
uv sync
```

Before committing changes, run:

```bash
uv run ruff check .
uv run pytest
```

Do not commit:

* `.env`
* API keys
* passwords
* `.idea/`
* `.venv/`
* other local or secret configuration files
