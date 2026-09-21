from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from events_aggregator.api.events import router as events_router
from events_aggregator.api.sync import router as sync_router
from events_aggregator.api.tickets import router as tickets_router
from events_aggregator.clients.exceptions import ProviderNotFoundError

app = FastAPI()

app.include_router(sync_router)
app.include_router(events_router)
app.include_router(tickets_router)


@app.exception_handler(ProviderNotFoundError)
async def provider_not_found_handler(
    request: Request,
    exc: ProviderNotFoundError,
):
    """Handle not found errors from the Events Provider"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Event not found"},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """Handle request validation errors"""
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )


@app.get("/api/health")
async def health():
    """Return application health status"""
    return {"status": "ok"}
