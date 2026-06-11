import os
import dotenv
from aiohttp import ClientSession
from schemas import EventsApiResponse
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
    ) -> EventsApiResponse:
    page = page
    page_size = page_size
    url = f'{base_url}{"/api/events/"}'
    events = await get_http(
        client,
        url=url, 
        params = {'changed_at': date_from})
    events_json = await events.json()
    events_valid = EventsApiResponse(events_json)
    while events_valid.next:
        new_events = await get_http(
                client,
                url=url, 
                params = {'changed_at': date_from})
        new_events_json = await new_events.json()
        new_events_valid = EventsApiResponse(new_events_json)
        events_valid.model_extend(new_events_valid)
    return events_valid
