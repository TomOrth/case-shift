from typing import Protocol
import pypdf
from .models import ParsedArtifact, ParsedPage

class DocumentParser(Protocol):
    def parse(self, doc_id: str, file_path: str) -> ParsedArtifact:
        ...

class PyPDFParser:
    """A concrete parser implementation using pypdf."""
    def parse(self, doc_id: str, file_path: str) -> ParsedArtifact:
        pages = []
        is_empty = True
        is_low_quality = False

        try:
            with open(file_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                num_pages = len(reader.pages)

                for i in range(num_pages):
                    page = reader.pages[i]
                    text = page.extract_text() or ""
                    clean_text = text.strip()

                    if clean_text:
                        is_empty = False
                        pages.append(ParsedPage(page_number=i+1, text=clean_text, is_blank=False))
                    else:
                        pages.append(ParsedPage(page_number=i+1, text="", is_blank=True))

        except (FileNotFoundError, Exception):
            return ParsedArtifact(
                doc_id=doc_id,
                pages=[],
                total_pages=0,
                is_empty=True,
                is_low_quality=True
            )

        # Basic low quality detection: non-empty but very few extracted characters across multiple pages
        if not is_empty and sum(len(p.text) for p in pages) < 20 and len(pages) > 0:
            is_low_quality = True

        return ParsedArtifact(
            doc_id=doc_id,
            pages=pages,
            total_pages=len(pages),
            is_empty=is_empty,
            is_low_quality=is_low_quality
        )

class DummyPDFParser:
    """A dummy parser implementation for testing text extraction without real PDFs."""
    def parse(self, doc_id: str, file_path: str) -> ParsedArtifact:
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

        page_texts = content.split('\x0c')

        for i, text in enumerate(page_texts):
            clean_text = text.strip()
            if clean_text:
                is_empty = False
                pages.append(ParsedPage(page_number=i+1, text=clean_text, is_blank=False))
            else:
                pages.append(ParsedPage(page_number=i+1, text="", is_blank=True))

        if not is_empty and sum(len(p.text) for p in pages) < 20 and len(pages) > 0:
            is_low_quality = True

        return ParsedArtifact(
            doc_id=doc_id,
            pages=pages,
            total_pages=len(pages),
            is_empty=is_empty,
            is_low_quality=is_low_quality
        )
