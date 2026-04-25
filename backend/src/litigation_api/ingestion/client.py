import logging
import httpx
from typing import AsyncGenerator, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class CRLCAClientError(Exception):
    """Base exception for CRLCA client errors."""
    pass

class CRLCAClient:
    def __init__(self, base_url: str = "https://api.clearinghouse.net/api/v2p1/", timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout
        self.headers = {"User-Agent": "Case-Shift-Ingestion/1.0"}
        self._client = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.headers,
            follow_redirects=True
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("CRLCAClient must be used as an async context manager")
        return self._client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError, CRLCAClientError)),
        reraise=True
    )
    async def _fetch_url(self, url: str) -> Dict[str, Any]:
        """Fetch a specific URL with retry logic."""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching {url}: {e.response.status_code}")
            raise CRLCAClientError(f"HTTP error fetching {url}: {e}") from e
        except httpx.RequestError as e:
            logger.error(f"Request error fetching {url}: {e}")
            raise CRLCAClientError(f"Request error fetching {url}: {e}") from e

    async def fetch_cases_paginated(self, start_url: str = "cases/") -> AsyncGenerator[Dict[str, Any], None]:
        """Fetch all cases from the CRLCA API using pagination."""
        url = start_url
        while url:
            data = await self._fetch_url(url)
            for case in data.get("results", []):
                yield case

            # The CRLCA API provides pagination URLs
            url = data.get("next")

    async def fetch_case_details(self, case_id: int) -> Dict[str, Any]:
        """Fetch details for a specific case."""
        return await self._fetch_url(f"cases/{case_id}/")

    async def fetch_case_documents(self, case_id: int) -> AsyncGenerator[Dict[str, Any], None]:
        """Fetch all documents for a specific case."""
        url = f"cases/{case_id}/documents/"
        while url:
            data = await self._fetch_url(url)
            for document in data.get("results", []):
                yield document
            url = data.get("next")

    async def fetch_case_dockets(self, case_id: int) -> AsyncGenerator[Dict[str, Any], None]:
        """Fetch all dockets for a specific case."""
        url = f"cases/{case_id}/dockets/"
        while url:
            data = await self._fetch_url(url)
            for docket in data.get("results", []):
                yield docket
            url = data.get("next")

    async def download_file(self, url: str) -> bytes:
        """Download a raw file from a URL with retries."""
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError, CRLCAClientError)),
            reraise=True
        )
        async def _download() -> bytes:
            try:
                # We use the existing client; if url is absolute, httpx handles it correctly
                response = await self.client.get(url)
                response.raise_for_status()
                return response.read()
            except httpx.HTTPStatusError as e:
                raise CRLCAClientError(f"HTTP error downloading {url}: {e}") from e
            except httpx.RequestError as e:
                raise CRLCAClientError(f"Request error downloading {url}: {e}") from e

        return await _download()
