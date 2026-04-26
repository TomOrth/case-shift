import pytest
from reportlab.pdfgen import canvas
from worker.parsing.parser import PyPDFParser

def create_pdf(file_path, pages_text):
    c = canvas.Canvas(file_path)
    for text in pages_text:
        c.drawString(100, 750, text)
        c.showPage()
    c.save()

@pytest.fixture
def parser():
    return PyPDFParser()

def test_pypdf_parser_with_content(tmp_path, parser):
    test_file = tmp_path / "test.pdf"
    try:
        from reportlab.pdfgen import canvas
    except ImportError:
        pytest.skip("reportlab not installed, skipping real pdf creation test")

    create_pdf(str(test_file), ["Page 1 content", "Page 2 content"])

    artifact = parser.parse("doc-123", str(test_file))

    assert artifact.doc_id == "doc-123"
    assert artifact.total_pages == 2
    assert not artifact.is_empty
    assert not artifact.is_low_quality
    assert len(artifact.pages) == 2
    assert artifact.pages[0].page_number == 1
    assert "Page 1 content" in artifact.pages[0].text
    assert artifact.pages[1].page_number == 2
    assert "Page 2 content" in artifact.pages[1].text

def test_pypdf_parser_missing_file(parser):
    artifact = parser.parse("doc-123", "does_not_exist.pdf")

    assert artifact.doc_id == "doc-123"
    assert artifact.total_pages == 0
    assert artifact.is_empty
    assert artifact.is_low_quality
