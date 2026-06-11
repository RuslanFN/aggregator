from fastapi import APIRouter, Request, Depends
from schemas import GetEventsParams, EventsApiResponse
from API_utils import get_http
from dotenv import load_dotenv
import os

router = APIRouter()

base_url = os.getenv('BASE_URL')

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/events")
async def events(
    request: Request,
    request_params: GetEventsParams = Depends()):
    date_from = request_params.date_from
    page = request_params.page
    page_size = request_params.page_size
    start_with = ((page-1)*page_size) % 10
    real_page = (page*page_size-1) // 10
    client = request.app.state.http_client
    url = f'{base_url}{"/api/events/"}'
    events = await get_http(
        client,
        url=url, 
        params = {'changed_at': date_from})
    
    for _ in range(real_page):
        if events['next']:
            events = await get_http(
                    client,
                    url=events['next'], 
                    params = {'changed_at': date_from})
        

    ans = await events.json()
    return ans
