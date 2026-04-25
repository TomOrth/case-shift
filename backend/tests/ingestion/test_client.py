import pytest
import httpx
from unittest.mock import AsyncMock, patch
import pytest_asyncio

from litigation_api.ingestion.client import CRLCAClient, CRLCAClientError

@pytest_asyncio.fixture
async def client():
    async with CRLCAClient() as c:
        yield c

@pytest.mark.asyncio
async def test_fetch_cases_paginated(client):
    mock_responses = [
        {"results": [{"id": 1, "name": "Case 1"}], "next": "cases/?page=2"},
        {"results": [{"id": 2, "name": "Case 2"}], "next": None}
    ]

    with patch.object(client, "_fetch_url", side_effect=mock_responses) as mock_fetch:
        cases = []
        async for case in client.fetch_cases_paginated():
            cases.append(case)

        assert len(cases) == 2
        assert cases[0]["name"] == "Case 1"
        assert cases[1]["name"] == "Case 2"
        assert mock_fetch.call_count == 2

@pytest.mark.asyncio
async def test_fetch_case_details(client):
    mock_response = {"id": 1, "name": "Case 1"}
    with patch.object(client, "_fetch_url", return_value=mock_response):
        case = await client.fetch_case_details(1)
        assert case["id"] == 1
        assert case["name"] == "Case 1"

@pytest.mark.asyncio
async def test_fetch_case_documents(client):
    mock_responses = [
        {"results": [{"id": 10, "document_type": "Complaint"}], "next": None}
    ]

    with patch.object(client, "_fetch_url", side_effect=mock_responses):
        docs = []
        async for doc in client.fetch_case_documents(1):
            docs.append(doc)

        assert len(docs) == 1
        assert docs[0]["document_type"] == "Complaint"

@pytest.mark.asyncio
async def test_download_file(client):
    mock_content = b"pdfcontent"

    class MockResponse:
        def __init__(self, content):
            self._content = content
        def raise_for_status(self):
            pass
        def read(self):
            return self._content

    with patch.object(client.client, "get", return_value=MockResponse(mock_content)) as mock_get:
        content = await client.download_file("http://example.com/file.pdf")
        assert content == mock_content
        mock_get.assert_called_once_with("http://example.com/file.pdf")

@pytest.mark.asyncio
async def test_fetch_url_retry_logic(client):
    class MockErrorResponse:
        status_code = 500

    class MockSuccessResponse:
        def raise_for_status(self):
            pass
        def json(self):
            return {"success": True}

    side_effects = [
        httpx.HTTPStatusError("Error", request=AsyncMock(), response=MockErrorResponse()),
        httpx.HTTPStatusError("Error", request=AsyncMock(), response=MockErrorResponse()),
        MockSuccessResponse()
    ]

    with patch.object(client.client, "get", side_effect=side_effects) as mock_get:
        with patch("litigation_api.ingestion.client.logger.error") as mock_logger:
            result = await client._fetch_url("test_url")
            assert result == {"success": True}
            assert mock_get.call_count == 3
            assert mock_logger.call_count == 2
