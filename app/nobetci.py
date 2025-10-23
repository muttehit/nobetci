import asyncio
from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from app.tasks.marznode import start_marznode_tasks
from app.telegram_bot import build_telegram_bot
from app.utils.panel import get_marznodes

from . import __version__

from app.config import (DEBUG, DOCS, PANEL_ADDRESS, PANEL_CUSTOM_NODES, PANEL_PASSWORD, PANEL_USERNAME,
                        UVICORN_HOST, UVICORN_PORT, UVICORN_SSL_CERTFILE, UVICORN_SSL_KEYFILE, UVICORN_UDS)
from app.routes import api_router
from app.tasks.nodes import nodes_startup

from fastapi.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    asyncio.create_task(build_telegram_bot())

    await nodes_startup()

    asyncio.create_task(start_marznode_tasks())

    yield

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

app = FastAPI(
    title="NobetciAPI",
    description="Xray ip limit",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs" if DOCS else None,
    redoc_url="/redoc" if DOCS else None,
)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    details = {}
    for error in exc.errors():
        details[error["loc"][-1]] = error.get("msg")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": details}),
    )


async def main():
    cfg = Config(
        app=app,
        host=UVICORN_HOST,
        port=UVICORN_PORT,
        uds=(None if DEBUG else UVICORN_UDS),
        ssl_certfile=UVICORN_SSL_CERTFILE,
        ssl_keyfile=UVICORN_SSL_KEYFILE,
        workers=1,
        reload=DEBUG,
        log_level=logging.DEBUG if DEBUG else logging.INFO,
    )
    server = Server(cfg)
    await server.serve()
