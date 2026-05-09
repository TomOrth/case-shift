import re
from typing import Optional
import abc

SUPPORTED_DOCUMENT_TYPES = {"Complaint", "Opinion/Order", "Settlement"}

class ClassificationProvider(abc.ABC):
    @abc.abstractmethod
    def classify(self, text: str, title: Optional[str] = None, docket_title: Optional[str] = None) -> Optional[str]:
        pass

class DocumentClassifier:
    """
    Classifies documents into the supported v1 filing types using deterministic rules
    with explicit fallback behavior.
    """
    def __init__(self, fallback_provider: Optional[ClassificationProvider] = None):
        self.fallback_provider = fallback_provider
        self.complaint_re = re.compile(r'\bcomplaint\b', re.IGNORECASE)
        self.opinion_order_re = re.compile(r'\b(opinion|order|decision|ruling)\b', re.IGNORECASE)
        self.settlement_re = re.compile(r'\b(settlement|consent decree|stipulation|agreement)\b', re.IGNORECASE)

    def classify(self, document_type: Optional[str] = None, title: Optional[str] = None, docket_title: Optional[str] = None, text_content: Optional[str] = None) -> str:
        # 1. Exact match on API provided document type
        if document_type in SUPPORTED_DOCUMENT_TYPES:
            return document_type

        # 2. Heuristics on available fields
        def _apply_heuristics(text: str) -> Optional[str]:
            if self.opinion_order_re.search(text):
                return "Opinion/Order"
            if self.settlement_re.search(text):
                return "Settlement"
            if self.complaint_re.search(text):
                return "Complaint"
            return None

        if document_type:
            result = _apply_heuristics(document_type)
            if result:
                return result

        if title:
            result = _apply_heuristics(title)
            if result:
                return result

        if docket_title:
            result = _apply_heuristics(docket_title)
            if result:
                return result

        # 3. Optional AI Fallback
        if self.fallback_provider:
            result = self.fallback_provider.classify(
                text=text_content or "",
                title=title,
                docket_title=docket_title
            )
            if result in SUPPORTED_DOCUMENT_TYPES:
                return result

        # 4. Unknown fallback
        return "Unknown"

# Default instance to be used across the ingestion module
default_classifier = DocumentClassifier()

def classify_document(document_type: Optional[str] = None, title: Optional[str] = None, docket_title: Optional[str] = None, text_content: Optional[str] = None) -> str:
    """
    Convenience function that uses the default DocumentClassifier.
    """
    return default_classifier.classify(document_type=document_type, title=title, docket_title=docket_title, text_content=text_content)
