"""
Builds the data payload shown on the app’s home page.
Everything is async, pure-python, no Celery needed.
"""

import datetime as _dt
from datetime import datetime, timezone
from typing import Dict, List, Tuple
from dateutil import parser as _p

from libs.database.youtube.videos import get_videos_by_channel_id, get_videos_by_ids
from libs.database.youtube.analysis import get_analyses_by_video_ids

# ---------------------------------------------------------------------------


async def _collect_user_video_ids(
    channel_ids: List[str], since: _dt.datetime
) -> List[str]:
    vids: List[str] = []
    for cid in channel_ids:
        for v in await get_videos_by_channel_id(cid):
            ts = _p.isoparse(v["publish_time"])
            if ts >= since:
                vids.append(str(v["_id"]))
    return vids


async def build_homepage_summary(
    channel_ids: List[str], period_days: int = 30, trend_count: int = 10
) -> Dict:
    cutoff = datetime.now(timezone.utc) - _dt.timedelta(days=period_days)
    video_ids = await _collect_user_video_ids(channel_ids, cutoff)
    if not video_ids:
        return {"detail": "no analysed videos in selected window"}

    analyses = await get_analyses_by_video_ids(video_ids)
    if not analyses:
        return {"detail": "no analyses in DB for selected videos"}

    a_map = {str(a["comment_id"]): a["analysis"] for a in analyses}
    vids = {v["id"]: v for v in await get_videos_by_ids(video_ids)}
    valid = set(a_map) & set(vids)
    if not valid:
        return {"detail": "no analysed videos in selected window"}
    vids = {vid: vids[vid] for vid in valid}

    # sums for overall & creator breakdown
    sum_overall = {"positive": 0, "neutral": 0, "negative": 0}
    sum_creator = {"positive": 0, "neutral": 0, "negative": 0}

    trend_video = []  # will hold (timestamp, breakdown_dict)
    trend_creator = []

    best = (-1, None)
    worst = (2, None)

    for vid, meta in vids.items():
        s = a_map[vid]["sentiments"]

        # accumulate sums
        for k in sum_overall:
            sum_overall[k] += s["video"][k] + s["creator"][k] + s["topic"][k]
            sum_creator[k] += s["creator"][k]

        # store full breakdown in trend
        ts = _p.isoparse(meta["publish_time"])
        trend_video.append((ts, s["video"]))
        trend_creator.append((ts, s["creator"]))

        # pick best/worst by positive%
        overall_pos = (
            s["video"]["positive"] + s["creator"]["positive"] + s["topic"]["positive"]
        ) / 3.0
        if overall_pos > best[0]:
            best = (overall_pos, vid)
        if overall_pos < worst[0] or worst[1] is None:
            worst = (overall_pos, vid)

    n = len(vids)
    # for overall, each video contributes 3 categories
    avg_overall = {k: round(sum_overall[k] / (n * 3), 1) for k in sum_overall}
    avg_creator = {k: round(sum_creator[k] / n, 1) for k in sum_creator}

    # helper to turn list of tuples into list of dicts
    def make_series(arr):
        arr.sort(key=lambda x: x[0])
        out = []
        for ts, breakdown in arr[-trend_count:]:
            point = {"timestamp": ts.isoformat()}
            point.update(breakdown)
            out.append(point)
        return out

    result = {
        "period_days": period_days,
        "samples": n,
        "overall_sentiment_breakdown": avg_overall,
        "creator_sentiment_breakdown": avg_creator,
        "trend": {
            "video": make_series(trend_video),
            "creator": make_series(trend_creator),
        },
        "best_video": (
            (vids[best[1]] | {"overall_positive": round(best[0], 1)})
            if best[1]
            else None
        ),
        "worst_video": (
            (vids[worst[1]] | {"overall_positive": round(worst[0], 1)})
            if worst[1]
            else None
        ),
    }
    return result
