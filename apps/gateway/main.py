# apps/gateway/main.py
#
# Hardened FastAPI reverse-proxy for public traffic:
#   * strips hop-by-hop headers
#   * enforces a maximum request size
#   * throttles abuse with a tiny per-IP token bucket

import os
import time
from typing import Dict

import httpx
from fastapi import FastAPI, Request, Response, HTTPException, status

app = FastAPI(title="Gateway")

# ---------------------------------------------------------------------------
# configuration knobs (env-controlled)
# ---------------------------------------------------------------------------
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://users:8001")
YOUTUBE_SERVICE_URL = os.getenv("YOUTUBE_SERVICE_URL", "http://youtube:8002")
MAX_REQUEST_BYTES = int(os.getenv("MAX_REQUEST_BYTES", 1 * 1024 * 1024))  # 1 MiB
REQUESTS_PER_MINUTE = int(os.getenv("REQUESTS_PER_MINUTE", 60))

# ---------------------------------------------------------------------------
# simple in-memory token bucket by client IP
# ---------------------------------------------------------------------------
_buckets: Dict[str, Dict[str, float]] = {}  # {ip: {"tokens": float, "ts": float}}


def _is_allowed(ip: str) -> bool:
    """
    Token-bucket: refills at REQUESTS_PER_MINUTE per 60 s.
    """
    now = time.time()
    bucket = _buckets.setdefault(ip, {"tokens": REQUESTS_PER_MINUTE, "ts": now})
    # refill
    elapsed = now - bucket["ts"]
    bucket["tokens"] = min(
        REQUESTS_PER_MINUTE,
        bucket["tokens"] + (elapsed * REQUESTS_PER_MINUTE / 60.0),
    )
    bucket["ts"] = now
    if bucket["tokens"] >= 1.0:
        bucket["tokens"] -= 1.0
        return True
    return False


# ---------------------------------------------------------------------------
# hop-by-hop headers blacklist (RFC 2616 §13.5.1)
# ---------------------------------------------------------------------------
_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


def _scrub_headers(headers) -> dict:
    """
    Remove hop-by-hop headers from the incoming request before proxying.
    """
    return {
        k.decode().lower(): v.decode()
        for k, v in headers
        if k.decode().lower() not in _HOP_HEADERS
    }


# ---------------------------------------------------------------------------
# generic proxy helper
# ---------------------------------------------------------------------------
async def _proxy_request(
    service_url: str, full_path: str, request: Request
) -> Response:
    # rate-limit
    client_ip = request.headers.get("x-forwarded-for", request.client.host)
    if not _is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate limit exceeded"
        )

    # body size guard
    body_bytes = await request.body()
    if len(body_bytes) > MAX_REQUEST_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"payload too big (>{MAX_REQUEST_BYTES} bytes)",
        )

    # scrub headers
    clean_headers = _scrub_headers(request.headers.raw)

    async with httpx.AsyncClient(
        base_url=service_url,
        timeout=30.0,
    ) as client:
        proxied_req = client.build_request(
            request.method,
            f"/{full_path}",
            headers=clean_headers,
            params=request.query_params,
            content=body_bytes,
        )
        try:
            proxied_resp = await client.send(proxied_req, stream=True)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        raw_body = await proxied_resp.aread()
        # copy response headers but *also* strip hop-by-hop ones
        resp_headers = {
            k: v
            for k, v in proxied_resp.headers.items()
            if k.lower() not in _HOP_HEADERS
        }
        return Response(
            content=raw_body,
            status_code=proxied_resp.status_code,
            headers=resp_headers,
        )


# ---------------------------------------------------------------------------
# proxy routes
# ---------------------------------------------------------------------------


@app.api_route(
    "/users/{full_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
async def proxy_users(full_path: str, request: Request):
    return await _proxy_request(USERS_SERVICE_URL, full_path, request)


@app.api_route(
    "/youtube/{full_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
async def proxy_youtube(full_path: str, request: Request):
    return await _proxy_request(YOUTUBE_SERVICE_URL, full_path, request)
