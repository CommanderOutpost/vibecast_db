# apps/youtube/worker.py

import os
from celery import Celery
from config.config import settings
from libs.youtube.get_all_videos_from_channel import get_all_videos_from_channel
from libs.youtube.get_youtube_comments import get_youtube_comments

# 1) Pull your Redis host/port/db out of settings
REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_DB = settings.REDIS_DB

# 2) If you want to override via CELERY_BROKER_URL in env/.env, respect that first:
broker_url = (
    settings.CELERY_BROKER_URL or f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
)
backend_url = (
    settings.CELERY_BACKEND_URL or f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB + 1}"
)

celery = Celery(
    "youtube_worker",
    broker=broker_url,
    backend=backend_url,
)
celery.conf.update(task_track_started=True, task_serializer="json")


@celery.task(name="youtube.sync_channel")
def sync_channel_task(channel_id: str):
    import asyncio

    asyncio.run(
        get_all_videos_from_channel(
            api_key=settings.YOUTUBE_API_KEY,
            channel_id=channel_id,
        )
    )


@celery.task(name="youtube.grab_comments")
def grab_comments_task(video_id: str, limit: int):
    import asyncio

    asyncio.run(
        get_youtube_comments(
            api_key=settings.YOUTUBE_API_KEY,
            video_id=video_id,
            max_comments=limit,
        )
    )
