from aiohttp import ClientSession
from schemas import EventsApiResponse, EventApiResponse
from typing import List
import os
import dotenv
from config import get_logger

logger = get_logger(__name__)
dotenv.load_dotenv()

base_url = os.getenv("BASE_URL")
x_api_key = os.getenv("X_API_KEY")

async def get_http(
    client: ClientSession, 
    url: str, 
    params: dict = None) -> dict:
    events = await client.get(
        url,
        headers = {'x-api-key': x_api_key},
        params = params
    )
    events_json = await events.json()
    return events_json

async def get_all_events(
    client: ClientSession, 
    date_from: str = '2000-01-01',
    ) -> List[EventApiResponse]:
    url = f'{base_url}{"/api/events/"}'
    events_json = await get_http(
        client,
        url=url, 
        params = {'changed_at': date_from})
    events_valid = EventsApiResponse(**events_json)
    results = [] 
    results.extend(events_valid.results)
    
    while events_valid.next:
        logger.info(events_valid.next)
        events_json = await get_http(
                client,
                url=events_valid.next)
        events_valid = EventsApiResponse(**events_json)
        results.extend(events_valid.results)
    return results
