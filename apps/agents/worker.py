import asyncio
from celery import Celery
from config.config import settings
from libs.agents.comments_analyzer.comments_analyzer import analyze_and_store_comments

broker = (
    settings.CELERY_BROKER_URL
    or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
)
backend = (
    settings.CELERY_BACKEND_URL
    or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB+1}"
)

celery = Celery("agents_worker", broker=broker, backend=backend)
celery.conf.update(task_track_started=True, task_serializer="json")


@celery.task(name="agents.analyze_comments")
def analyze_comments_task(video_id: str):
    asyncio.run(analyze_and_store_comments(video_id))
