from fastapi import FastAPI

from events_aggregator.core.config import settings


app = FastAPI()


@app.get('/api/health')
async def health():
    return {'status': 'ok'}
