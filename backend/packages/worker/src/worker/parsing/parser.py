from typing import Protocol, List
from .models import ParsedArtifact, ParsedPage

class DocumentParser(Protocol):
    def parse(self, doc_id: str, file_path: str) -> ParsedArtifact:
        ...

class DummyPDFParser:
    """A dummy parser implementation for testing text extraction and parsing."""
    def parse(self, doc_id: str, file_path: str) -> ParsedArtifact:
        # In a real scenario, this would use PyMuPDF or pdfplumber
        # This dummy implementation just creates an artifact from the string content of a file
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            return ParsedArtifact(
                doc_id=doc_id,
                pages=[],
                total_pages=0,
                is_empty=True,
                is_low_quality=True
            )

        pages = []
        is_empty = True
        is_low_quality = False

        # very rudimentary mock page splitting
        page_texts = content.split('\x0c') # form feed character for page breaks

        for i, text in enumerate(page_texts):
            clean_text = text.strip()
            if clean_text:
                is_empty = False
                pages.append(ParsedPage(page_number=i+1, text=clean_text, is_blank=False))
            else:
                pages.append(ParsedPage(page_number=i+1, text="", is_blank=True))

        # Mock low quality detection if very few characters but multiple pages
        if not is_empty and sum(len(p.text) for p in pages) < 20 and len(pages) > 0:
            is_low_quality = True

        return ParsedArtifact(
            doc_id=doc_id,
            pages=pages,
            total_pages=len(pages),
            is_empty=is_empty,
            is_low_quality=is_low_quality
        )
