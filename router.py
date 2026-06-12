from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi import status, Query
from schemas import GetEventsParams, EventsApiResponse, EventsResponse
from service import get_all_events, EventService
from API_utils import get_http
from database import get_session
from dotenv import load_dotenv
from datetime import datetime
import os
from config import get_logger

logger = get_logger(__name__)

router = APIRouter()

base_url = os.getenv('BASE_URL')

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/events", response_model=EventsResponse)
async def events(
    request: Request,
    params: GetEventsParams=Query(),
    session=Depends(get_session)):
    event_service = EventService(session)
    date_from = datetime.strptime(params.date_from, "%Y-%m-%d")
    base_url = str(request.base_url).rstrip("/")
    ans = await event_service.get_events_later_than(
        base_url,
        date_from=date_from,
        page=params.page,
        page_size=params.page_size
        )
    return ans

@router.post('/trigger')
async def sync_data(request: Request, session=Depends(get_session)):
    client = request.app.state.http_client
    try:
        event_service = EventService(session)
        await event_service.sync_events(client)
        return {'status': 'ok'}
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ошибка синхронизации'
        )
