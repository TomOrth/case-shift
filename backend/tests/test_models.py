import pytest
from pydantic import ValidationError
from app.models.domain import Case, Document, DocketEntry, Chunk

def test_chunk_model():
    chunk = Chunk(
        chunk_id="chunk-1",
        doc_id="doc-1",
        case_id="case-1",
        chunk_index=0,
        text="This is a test chunk.",
        page_start=1,
        page_end=2,
    )
    assert chunk.chunk_id == "chunk-1"
    assert chunk.doc_id == "doc-1"
    assert chunk.case_id == "case-1"
    assert chunk.chunk_index == 0
    assert chunk.text == "This is a test chunk."
    assert chunk.page_start == 1
    assert chunk.page_end == 2

def test_document_model():
    doc = Document(
        doc_id="doc-101",
        case_id="case-303",
        entry_id="entry-202",
        title="Test Complaint",
        document_type="complaint",
        filed_at="2023-10-01",
        author_type="plaintiff",
        disposition="pending",
        summary="A test complaint summary.",
    )
    assert doc.doc_id == "doc-101"
    assert doc.case_id == "case-303"
    assert doc.entry_id == "entry-202"
    assert doc.title == "Test Complaint"
    assert doc.document_type == "complaint"
    assert doc.filed_at == "2023-10-01"
    assert doc.author_type == "plaintiff"
    assert doc.disposition == "pending"
    assert doc.summary == "A test complaint summary."

def test_docket_entry_model():
    entry = DocketEntry(
        entry_id="entry-202",
        case_id="case-303",
        docket_number="1:23-cv-00001",
        filed_at="2023-10-01",
        title="Complaint filed",
        entry_type="complaint",
        source_url="https://example.com/docket/202",
    )
    assert entry.entry_id == "entry-202"
    assert entry.case_id == "case-303"
    assert entry.docket_number == "1:23-cv-00001"
    assert entry.filed_at == "2023-10-01"
    assert entry.title == "Complaint filed"
    assert entry.entry_type == "complaint"
    assert str(entry.source_url) == "https://example.com/docket/202"

def test_case_model():
    case = Case(
        case_id="case-303",
        case_name="Test v. Test",
        court="USDC",
        jurisdiction="S.D. Florida",
        filed_date="2023-10-01",
        closed_date="2023-11-01",
        status="open",
    )
    assert case.case_id == "case-303"
    assert case.case_name == "Test v. Test"
    assert case.court == "USDC"
    assert case.jurisdiction == "S.D. Florida"
    assert case.filed_date == "2023-10-01"
    assert case.closed_date == "2023-11-01"
    assert case.status == "open"

def test_legacy_placeholder_fields_are_rejected():
    with pytest.raises(ValidationError):
        Document(
            id=101,
            title="Test Complaint",
            file="not-a-url",
            document_type="Complaint"
        )
