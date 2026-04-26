import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from litigation_api.ingestion.pipeline import IngestionPipeline
from litigation_api.ingestion.client import CRLCAClient

@pytest.fixture
def mock_s3_client():
    with patch("boto3.client") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_crlca_client():
    client = CRLCAClient()
    client.fetch_case_details = AsyncMock()
    client.fetch_case_dockets = AsyncMock()
    client.fetch_case_documents = AsyncMock()
    client.download_file = AsyncMock()
    return client

@pytest.fixture
def pipeline(mock_s3_client, mock_crlca_client):
    # Mocking _ensure_bucket_async so it doesn't fail on init
    p = IngestionPipeline(
        s3_endpoint_url="http://localhost",
        s3_bucket_name="test-bucket",
        client=mock_crlca_client
    )
    p._ensure_bucket_async = AsyncMock()
    return p

@pytest.mark.asyncio
async def test_fetch_and_normalize_case_supported_document(pipeline, mock_crlca_client, mock_s3_client):
    # Setup mocks
    mock_crlca_client.fetch_case_details.return_value = {
        "id": 1, "name": "Test Case", "court": "Federal Court"
    }

    async def mock_dockets(*args, **kwargs):
        yield {"id": 10, "docket_number_manual": "123"}
    mock_crlca_client.fetch_case_dockets = mock_dockets

    async def mock_documents(*args, **kwargs):
        yield {
            "id": 100,
            "document_type": "Complaint",
            "file": "http://example.com/doc.pdf"
        }
    mock_crlca_client.fetch_case_documents = mock_documents

    mock_crlca_client.download_file.return_value = b"pdf_bytes"

    # Run
    case, dockets, docs = await pipeline.fetch_and_normalize_case(1)

    # Assert
    pipeline._ensure_bucket_async.assert_awaited_once()
    assert case.case_id == "crlca_case_1"
    assert len(dockets) == 1
    assert dockets[0].entry_id == "crlca_docket_10"

    assert len(docs) == 1
    assert docs[0].doc_id == "crlca_doc_100"
    assert docs[0].document_type == "Complaint"
    assert docs[0].ingestion_status == "INGESTED"

    # Check download and upload
    mock_crlca_client.download_file.assert_called_once_with("http://example.com/doc.pdf")
    mock_s3_client.put_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="raw/crlca_doc_100.pdf",
        Body=b"pdf_bytes",
        ContentType="application/pdf"
    )

@pytest.mark.asyncio
async def test_fetch_and_normalize_case_unsupported_document(pipeline, mock_crlca_client, mock_s3_client):
    # Setup mocks
    mock_crlca_client.fetch_case_details.return_value = {
        "id": 1, "name": "Test Case", "court": "Federal Court"
    }

    async def mock_dockets(*args, **kwargs):
        yield {"id": 10, "docket_number_manual": "123"}
    mock_crlca_client.fetch_case_dockets = mock_dockets

    async def mock_documents(*args, **kwargs):
        yield {
            "id": 101,
            "document_type": "Correspondence",
            "file": "http://example.com/doc.pdf"
        }
    mock_crlca_client.fetch_case_documents = mock_documents

    # Run
    case, dockets, docs = await pipeline.fetch_and_normalize_case(1)

    # Assert
    assert len(docs) == 1
    assert docs[0].doc_id == "crlca_doc_101"
    assert docs[0].document_type == "Correspondence"
    assert docs[0].ingestion_status == "SKIPPED_UNSUPPORTED_TYPE"

    # Ensure no download or upload occurred
    mock_crlca_client.download_file.assert_not_called()
    mock_s3_client.put_object.assert_not_called()

@pytest.mark.asyncio
async def test_fetch_and_normalize_case_failed_download(pipeline, mock_crlca_client, mock_s3_client):
    # Setup mocks
    mock_crlca_client.fetch_case_details.return_value = {
        "id": 1, "name": "Test Case", "court": "Federal Court"
    }

    async def mock_dockets(*args, **kwargs):
        yield {"id": 10, "docket_number_manual": "123"}
    mock_crlca_client.fetch_case_dockets = mock_dockets

    async def mock_documents(*args, **kwargs):
        yield {
            "id": 100,
            "document_type": "Complaint",
            "file": "http://example.com/doc.pdf"
        }
    mock_crlca_client.fetch_case_documents = mock_documents

    mock_crlca_client.download_file.side_effect = Exception("Download failed")

    # Run
    case, dockets, docs = await pipeline.fetch_and_normalize_case(1)

    # Assert
    assert len(docs) == 1
    assert docs[0].doc_id == "crlca_doc_100"
    assert docs[0].ingestion_status == "FAILED_DOWNLOAD"

    mock_crlca_client.download_file.assert_called_once_with("http://example.com/doc.pdf")
    mock_s3_client.put_object.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_and_normalize_case_creates_synthetic_docket_when_missing(
    pipeline, mock_crlca_client
):
    mock_crlca_client.fetch_case_details.return_value = {
        "id": 1, "name": "Test Case", "court": "Federal Court", "filing_date": "2020-01-15"
    }

    async def mock_dockets(*args, **kwargs):
        if False:
            yield {}

    async def mock_documents(*args, **kwargs):
        yield {
            "id": 100,
            "document_type": "Correspondence",
            "file": "http://example.com/doc.pdf",
        }

    mock_crlca_client.fetch_case_dockets = mock_dockets
    mock_crlca_client.fetch_case_documents = mock_documents

    case, dockets, docs = await pipeline.fetch_and_normalize_case(1)

    assert case.case_id == "crlca_case_1"
    assert len(dockets) == 1
    assert dockets[0].entry_id == "crlca_docket_unknown_1"
    assert dockets[0].entry_type == "synthetic_case_document_anchor"
    assert docs[0].entry_id == dockets[0].entry_id


@pytest.mark.asyncio
async def test_fetch_and_normalize_case_uses_configured_client_when_not_injected(mock_s3_client):
    with patch("litigation_api.ingestion.pipeline.CRLCAClient") as mock_client_cls, \
         patch("litigation_api.ingestion.pipeline.settings") as mock_settings:
        mock_settings.crlca_base_url = "https://example.test/api/"
        mock_settings.crlca_timeout_seconds = 12.5
        mock_settings.crlca_token = "secret-token"

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.fetch_case_details = AsyncMock(return_value={"id": 1, "name": "Test Case", "court": "Federal Court"})

        async def mock_dockets(*args, **kwargs):
            if False:
                yield {}

        async def mock_documents(*args, **kwargs):
            if False:
                yield {}

        mock_client.fetch_case_dockets = mock_dockets
        mock_client.fetch_case_documents = mock_documents
        mock_client_cls.return_value = mock_client

        pipeline = IngestionPipeline(
            s3_endpoint_url="http://localhost",
            s3_bucket_name="test-bucket",
            client=None,
        )
        pipeline._ensure_bucket_async = AsyncMock()

        await pipeline.fetch_and_normalize_case(1)

        mock_client_cls.assert_called_once_with(
            base_url="https://example.test/api/",
            timeout=12.5,
            token="secret-token",
        )
