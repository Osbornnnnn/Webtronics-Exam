import sys

from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import UJSONResponse

sys.path.append("/opt/Webtronics/")
try:
    from . import config, controllers
    from .database.connection import init_models
except:
    from app import config, controllers
    from app.database.connection import init_models


async def http_exception(request: Request, exc: HTTPException):
    return UJSONResponse(status_code=exc.status_code, content=exc.detail)


exception_handlers = {HTTPException: http_exception}


application = FastAPI(
    title=config.TITLE,
    description=config.DESCRIPTION,
    version=config.VERSION,
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
    default_response_class=UJSONResponse,
    exception_handlers=exception_handlers,
)
application.include_router(controllers.auth)
application.include_router(controllers.posts)


@application.on_event(event_type="startup")
async def on_startup():
    await init_models()


@application.get("/docs", tags=["Other"])
async def get_documentation():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Documentation")
