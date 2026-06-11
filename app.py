from fastapi import FastAPI
from contextlib import asynccontextmanager
from router import router
import uvicorn
import aiohttp

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=10),
    )
    yield
    await app.state.http_client.close()

app = FastAPI(lifespan=lifespan)
app.include_router(
    router,
    prefix='/api')

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)