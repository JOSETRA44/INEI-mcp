import asyncio
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import httpx

from .config import INEISettings
from .exceptions import INEIAPIError, INEINotFoundError, INEITimeoutError

logger = logging.getLogger(__name__)

BASE_URL = "https://estadistapi.inei.gob.pe/api/v1"
USER_AGENT = "inei-mcp/0.1.0 (https://github.com/JOSETRA44/inei-mcp)"


@dataclass
class _CacheEntry:
    data: Any
    expires_at: datetime


class _TTLCache:
    def __init__(self, ttl_seconds: int) -> None:
        self._ttl = ttl_seconds
        self._store: dict[str, _CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if datetime.now() >= entry.expires_at:
            del self._store[key]
            return None
        return entry.data

    def set(self, key: str, data: Any) -> None:
        if self._ttl > 0:
            self._store[key] = _CacheEntry(
                data=data,
                expires_at=datetime.now() + timedelta(seconds=self._ttl),
            )


class INEIClient:
    """Async INEI Estadist API client with TTL cache and retry.

    The API is public (no auth required) — operates over HTTPS only.
    Some endpoints are slow (>10s) or intermittently unavailable; we use
    generous timeouts and expose this in tool descriptions.
    """

    def __init__(self, settings: INEISettings) -> None:
        self._settings = settings
        self._cache = _TTLCache(settings.cache_ttl)
        self._http: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "INEIClient":
        self._http = httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=httpx.Timeout(self._settings.timeout),
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            },
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._http:
            await self._http.aclose()
            self._http = None

    @staticmethod
    def _cache_key(path: str, params: dict | None) -> str:
        raw = path + (("?" + urlencode(sorted((params or {}).items()))) if params else "")
        return hashlib.sha256(raw.encode()).hexdigest()

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """GET request with TTL cache and exponential retry."""
        assert self._http is not None, "INEIClient must be used as async context manager"

        key = self._cache_key(path, params)
        cached = self._cache.get(key)
        if cached is not None:
            logger.debug("Cache hit: %s", path)
            return cached

        last_error: Exception | None = None
        for attempt in range(self._settings.max_retries + 1):
            try:
                response = await self._http.get(path, params=params)
            except httpx.TimeoutException as exc:
                raise INEITimeoutError(
                    f"Request timed out after {self._settings.timeout}s: {path}. "
                    "Some INEI endpoints are slow — try again or use a shorter query."
                ) from exc
            except httpx.ConnectError as exc:
                raise INEIAPIError(f"Cannot connect to INEI API: {exc}") from exc

            if response.status_code == 200:
                try:
                    data = response.json()
                except Exception as exc:
                    raise INEIAPIError(
                        f"Unexpected response format from INEI API: {response.text[:100]}"
                    ) from exc
                self._cache.set(key, data)
                return data

            if response.status_code == 404:
                raise INEINotFoundError(
                    f"Resource not found: {path}",
                    status_code=404,
                )

            if response.status_code in (500, 503, 429):
                wait = 2 ** (attempt + 1)
                logger.warning(
                    "INEI API error %d on %s; retrying in %ds",
                    response.status_code, path, wait,
                )
                last_error = INEIAPIError(
                    f"INEI API returned {response.status_code}",
                    status_code=response.status_code,
                )
                if attempt < self._settings.max_retries:
                    await asyncio.sleep(wait)
                    continue

            raise INEIAPIError(
                f"INEI API error {response.status_code}: {response.text[:200]}",
                status_code=response.status_code,
            )

        raise last_error or INEIAPIError("Request failed after retries")
