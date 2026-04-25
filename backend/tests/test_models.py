import pytest
from pydantic import ValidationError
from app.models.domain import Case, Document, DocketEntry, Chunk

def test_chunk_model():
    chunk = Chunk(
        id="chunk-1",
        document_id="doc-1",
        text="This is a test chunk.",
        page_number=1
    )
    assert chunk.id == "chunk-1"
    assert chunk.document_id == "doc-1"
    assert chunk.text == "This is a test chunk."
    assert chunk.page_number == 1

def test_document_model():
    doc = Document(
        id=101,
        title="Test Complaint",
        file="https://example.com/file.pdf",
        document_type="Complaint",
        date="2023-10-01",
        ecf_number="123"
    )
    assert doc.id == 101
    assert doc.title == "Test Complaint"
    assert str(doc.file) == "https://example.com/file.pdf"
    assert doc.document_type == "Complaint"
    assert doc.date == "2023-10-01"
    assert doc.ecf_number == "123"

def test_docket_entry_model():
    entry = DocketEntry(
        id=202,
        docket_number_manual="1:23-cv-00001",
        date_filed="2023-10-01"
    )
    assert entry.id == 202
    assert entry.docket_number_manual == "1:23-cv-00001"
    assert entry.date_filed == "2023-10-01"

def test_case_model():
    case = Case(
        id=303,
        name="Test v. Test",
        court="USDC",
        docket_status="Open",
        case_status="Active",
        filing_date="2023-10-01",
        summary="A test case summary."
    )
    assert case.id == 303
    assert case.name == "Test v. Test"
    assert case.court == "USDC"
    assert case.docket_status == "Open"
    assert case.case_status == "Active"
    assert case.filing_date == "2023-10-01"
    assert case.summary == "A test case summary."
    assert len(case.docket_entries) == 0
    assert len(case.documents) == 0

def test_invalid_document_model_url():
    with pytest.raises(ValidationError):
        Document(
            id=101,
            title="Test Complaint",
            file="not-a-url",
            document_type="Complaint"
        )
