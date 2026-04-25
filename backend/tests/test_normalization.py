from typing import Optional
from pydantic import HttpUrl

from litigation_api.ingestion.crlca_models import CRLCACase, CRLCADocket, CRLCADocument
from litigation_api.ingestion.normalization import normalize_date, normalize_case, normalize_docket_entry, normalize_document

def test_normalize_date():
    assert normalize_date(None) is None
    assert normalize_date("2023-10-25") == "2023-10-25"
    assert normalize_date("2023-10-25T14:30:00Z") == "2023-10-25"
    assert normalize_date("10/25/2023") == "2023-10-25"
    assert normalize_date("invalid date") == "invalid date"

def test_normalize_case():
    source = CRLCACase(
        id=123,
        name="Smith v. Jones",
        court="U.S. District Court",
        filing_date="2020-01-15"
    )
    case = normalize_case(source)
    assert case.case_id == "crlca_case_123"
    assert case.case_name == "Smith v. Jones"
    assert case.court == "U.S. District Court"
    assert case.jurisdiction == "Federal"
    assert case.filed_date == "2020-01-15"
    assert case.status is None

def test_normalize_docket_entry():
    source = CRLCADocket(
        id=456,
        docket_number_manual="1:20-cv-00123",
        date_filed="2020-01-15"
    )
    entry = normalize_docket_entry(source, "crlca_case_123")
    assert entry.entry_id == "crlca_docket_456"
    assert entry.case_id == "crlca_case_123"
    assert entry.docket_number == "1:20-cv-00123"
    assert entry.filed_at == "2020-01-15"
    assert entry.title == "Docket Entry 1:20-cv-00123"

def test_normalize_document():
    source = CRLCADocument(
        id=789,
        title="Initial Complaint",
        file="https://example.com/doc.pdf",
        document_type="Complaint",
        date="2020-01-15"
    )
    doc = normalize_document(source, "crlca_case_123", "crlca_docket_456")
    assert doc.doc_id == "crlca_doc_789"
    assert doc.case_id == "crlca_case_123"
    assert doc.entry_id == "crlca_docket_456"
    assert doc.document_type == "Complaint"
    assert doc.title == "Initial Complaint"
    assert doc.filed_at == "2020-01-15"
