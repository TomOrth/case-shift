import pytest
import os
from worker.parsing.parser import DummyPDFParser

def test_parser_with_content(tmp_path):
    parser = DummyPDFParser()
    test_file = tmp_path / "test.txt"
    test_file.write_text("Page 1 content\x0cPage 2 content")

    artifact = parser.parse("doc-123", str(test_file))

    assert artifact.doc_id == "doc-123"
    assert artifact.total_pages == 2
    assert not artifact.is_empty
    assert not artifact.is_low_quality
    assert len(artifact.pages) == 2
    assert artifact.pages[0].page_number == 1
    assert artifact.pages[0].text == "Page 1 content"
    assert artifact.pages[1].page_number == 2
    assert artifact.pages[1].text == "Page 2 content"

def test_parser_empty_content(tmp_path):
    parser = DummyPDFParser()
    test_file = tmp_path / "test.txt"
    test_file.write_text("   \x0c   ")

    artifact = parser.parse("doc-123", str(test_file))

    assert artifact.doc_id == "doc-123"
    assert artifact.total_pages == 2
    assert artifact.is_empty
    assert not artifact.is_low_quality
    assert len(artifact.pages) == 2
    assert artifact.pages[0].is_blank
    assert artifact.pages[1].is_blank

def test_parser_low_quality(tmp_path):
    parser = DummyPDFParser()
    test_file = tmp_path / "test.txt"
    test_file.write_text("a\x0cb")

    artifact = parser.parse("doc-123", str(test_file))

    assert artifact.doc_id == "doc-123"
    assert artifact.total_pages == 2
    assert not artifact.is_empty
    assert artifact.is_low_quality

def test_parser_missing_file():
    parser = DummyPDFParser()
    artifact = parser.parse("doc-123", "does_not_exist.txt")

    assert artifact.doc_id == "doc-123"
    assert artifact.total_pages == 0
    assert artifact.is_empty
    assert artifact.is_low_quality
