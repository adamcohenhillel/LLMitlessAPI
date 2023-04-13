"""Template App
"""
from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from fastapi.routing import APIRouter

from api.routes.demo import demo_router
from api.lifetime import register_shutdown_event, register_startup_event
from api.exception_handlers import register_exception_handlers


def get_app() -> FastAPI:
    """Get API app
    """
    app = FastAPI(
        title='Onboardy',
        description='Onboardy API',
        docs_url='/api/docs',
        redoc_url='/api/redoc',
        openapi_url='/api/openapi.json',
        default_response_class=UJSONResponse,
    )

    # Adds startup and shutdown events.
    register_startup_event(app)
    register_shutdown_event(app)
    register_exception_handlers(app)

    api_router = APIRouter()
    api_router.include_router(demo_router, prefix='/demo', tags=['demo'])

    app.include_router(router=api_router, prefix='/api')

    return app