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
    # Mocking _ensure_bucket so it doesn't fail on init
    with patch.object(IngestionPipeline, "_ensure_bucket"):
        return IngestionPipeline(
            s3_endpoint_url="http://localhost",
            s3_bucket_name="test-bucket",
            client=mock_crlca_client
        )

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
    assert case.case_id == "crlca_case_1"
    assert len(dockets) == 1
    assert dockets[0].entry_id == "crlca_docket_10"

    assert len(docs) == 1
    assert docs[0].doc_id == "crlca_doc_100"
    assert docs[0].document_type == "Complaint"

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
    assert docs[0].status == "SKIPPED_UNSUPPORTED_TYPE"

    # Ensure no download or upload occurred
    mock_crlca_client.download_file.assert_not_called()
    mock_s3_client.put_object.assert_not_called()
