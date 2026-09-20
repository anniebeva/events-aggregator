from fastapi import FastAPI

from events_aggregator.api.sync import router as sync_router

app = FastAPI()

app.include_router(sync_router)


@app.get('/api/health')
async def health():
    """Return application health status"""
    return {'status': 'ok'}
