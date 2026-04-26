import re
from typing import Optional
from datetime import datetime

from ..models.domain import Case, DocketEntry, Document
from .crlca_models import CRLCACase, CRLCADocket, CRLCADocument

# Pre-compiled regular expressions for date parsing
ISO_DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
US_DATE_RE = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")

def normalize_date(date_str: Optional[str]) -> Optional[str]:
    """Parse and normalize a date string into YYYY-MM-DD format."""
    if not date_str:
        return None

    try:
        # Try standard ISO parsing
        parsed = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        pass

    # Attempt simple regex match for YYYY-MM-DD
    match = ISO_DATE_RE.search(date_str)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

    # Attempt regex match for MM/DD/YYYY
    match_us = US_DATE_RE.search(date_str)
    if match_us:
        # Zero-pad month and day
        month = str(int(match_us.group(1))).zfill(2)
        day = str(int(match_us.group(2))).zfill(2)
        return f"{match_us.group(3)}-{month}-{day}"

    # If unparseable, return the original string to avoid data loss
    return date_str

def normalize_case(source: CRLCACase) -> Case:
    """Normalize a CRLCA Case into a Tier 1 Case domain model."""
    case_id = f"crlca_case_{source.id}"

    # We must provide a jurisdiction.
    jurisdiction = "Federal"
    if "State" in source.court or "County" in source.court:
        jurisdiction = "State"

    return Case(
        case_id=case_id,
        case_name=source.name,
        court=source.court,
        jurisdiction=jurisdiction,
        filed_date=normalize_date(source.filing_date),
        closed_date=None,
        status=source.docket_status or source.case_status
    )

def normalize_docket_entry(source: CRLCADocket, case_id: str) -> DocketEntry:
    """Normalize a CRLCA Docket into a Tier 1 DocketEntry domain model."""
    entry_id = f"crlca_docket_{source.id}"

    docket_num = None
    if source.docket_number_manual is not None:
        docket_num = str(source.docket_number_manual)
    elif source.docket_filing_number is not None:
        docket_num = str(source.docket_filing_number)

    title = f"Docket Entry {docket_num}" if docket_num else f"Docket Entry {source.id}"

    return DocketEntry(
        entry_id=entry_id,
        case_id=case_id,
        docket_number=docket_num,
        filed_at=normalize_date(source.date_filed),
        title=title,
        entry_type=None,
        source_url=None
    )

def normalize_document(source: CRLCADocument, case_id: str, entry_id: str) -> Document:
    """Normalize a CRLCA Document into a Tier 1 Document domain model."""
    doc_id = f"crlca_doc_{source.id}"

    title = source.title or source.description or f"Document {source.id}"
    doc_type = source.document_type
    if not doc_type:
        doc_type = "Unknown"

    return Document(
        doc_id=doc_id,
        case_id=case_id,
        entry_id=entry_id,
        document_type=doc_type,
        title=title,
        filed_at=normalize_date(source.date),
        author_type=None,
        disposition=None,
        summary=None,
        summary_embedding=None
    )
