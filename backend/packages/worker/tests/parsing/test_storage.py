import pytest
import os
import boto3
from moto import mock_aws
from worker.parsing.models import ParsedArtifact, ParsedPage
from worker.parsing.storage import ArtifactStorage

@pytest.fixture
def s3_setup():
    with mock_aws():
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-bucket')
        yield s3

def test_store_and_get_artifact(s3_setup):
    storage = ArtifactStorage(bucket_name='test-bucket')

    artifact = ParsedArtifact(
        doc_id="doc-456",
        pages=[ParsedPage(page_number=1, text="Hello world")],
        total_pages=1,
        is_empty=False,
        is_low_quality=False
    )

    # Store artifact
    key = storage.store_artifact(artifact)
    assert key == "parsed/doc-456.json"

    # Retrieve artifact
    retrieved = storage.get_artifact("doc-456")
    assert retrieved is not None
    assert retrieved.doc_id == "doc-456"
    assert len(retrieved.pages) == 1
    assert retrieved.pages[0].text == "Hello world"
    assert retrieved.total_pages == 1

def test_get_missing_artifact(s3_setup):
    storage = ArtifactStorage(bucket_name='test-bucket')
    retrieved = storage.get_artifact("missing-doc")
    assert retrieved is None
