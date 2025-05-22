# libs/tasks.py
#
# Imported by FastAPI app to off-load work to Celery without
# the API service importing Celery directly (keeps deps light).

from importlib import import_module

_worker = import_module("apps.youtube.worker")
celery_app = _worker.celery


def enqueue_sync_channel(channel_id: str):
    # Ensure we always send a JSON-safe string
    celery_app.send_task("youtube.sync_channel", args=[str(channel_id)], queue="youtube_queue")


def enqueue_grab_comments(video_id: str, limit: int):
    # video_id should already be a string, but we’ll str() it just in case
    celery_app.send_task("youtube.grab_comments", args=[str(video_id), limit], queue="youtube_queue")
