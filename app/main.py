import multiprocessing
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.api.main import api_router
from app.reservations.application.jobs.cancel_expired_reservations_job import cancel_expired_reservations_job
from app.settings import get_settings
from app.shared.infrastructure.events.rabbitmq_configurer_factory import RabbitMQConfigurerFactory

settings = get_settings()


def setup_jobs_scheduler() -> None:
    scheduler = BackgroundScheduler()
    scheduler.add_job(cancel_expired_reservations_job, "interval", minutes=1)
    scheduler.start()


def setup_event_subscribers() -> None:
    configurer = RabbitMQConfigurerFactory.create()
    configurer.start()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    setup_jobs_scheduler()

    subscriber_process = multiprocessing.Process(target=setup_event_subscribers)
    subscriber_process.start()

    yield

    subscriber_process.terminate()
    subscriber_process.join()


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)
app.include_router(api_router, prefix=settings.API_V1_STR)
