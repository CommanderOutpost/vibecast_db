from importlib import import_module

# import the Celery instance from our new agents worker
_worker = import_module("apps.agents.worker")
celery_app = _worker.celery


def enqueue_analyze_comments(video_id: str):
    """
    Queues analysis of comments for the given video_id on Celery.
    """
    celery_app.send_task("agents.analyze_comments", args=[str(video_id)])
