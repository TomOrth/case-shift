from litigation_api.ingestion.classification import DocumentClassifier, ClassificationProvider, classify_document

class MockFallbackProvider(ClassificationProvider):
    def classify(self, text: str, title: str | None = None, docket_title: str | None = None) -> str | None:
        if "secret model settlement" in (text or ""):
            return "Settlement"
        return None

def test_exact_match():
    classifier = DocumentClassifier()
    assert classifier.classify(document_type="Complaint") == "Complaint"
    assert classifier.classify(document_type="Opinion/Order") == "Opinion/Order"
    assert classifier.classify(document_type="Settlement") == "Settlement"

def test_heuristics_document_type():
    classifier = DocumentClassifier()
    assert classifier.classify(document_type="Amended Complaint") == "Complaint"
    assert classifier.classify(document_type="Final Order") == "Opinion/Order"
    assert classifier.classify(document_type="Consent Decree") == "Settlement"

def test_heuristics_title():
    classifier = DocumentClassifier()
    assert classifier.classify(title="First Amended Complaint") == "Complaint"
    assert classifier.classify(title="Decision on Motion to Dismiss") == "Opinion/Order"
    assert classifier.classify(title="Stipulation of Dismissal") == "Settlement"

def test_heuristics_docket_title():
    classifier = DocumentClassifier()
    assert classifier.classify(docket_title="Notice of Settlement") == "Settlement"

def test_heuristic_priority():
    classifier = DocumentClassifier()
    assert classifier.classify(title="Order Denying Motion to Amend Complaint") == "Opinion/Order"
    assert classifier.classify(title="Opinion on Motion to Dismiss Complaint") == "Opinion/Order"
    assert classifier.classify(title="Ruling on Plaintiff's Complaint") == "Opinion/Order"
    assert classifier.classify(title="Stipulation to Dismiss Complaint") == "Settlement"

def test_fallback_provider():
    classifier = DocumentClassifier(fallback_provider=MockFallbackProvider())
    assert classifier.classify(text_content="This is a secret model settlement.") == "Settlement"
    assert classifier.classify(text_content="Some other random text.") == "Unknown"

def test_unknown_fallback():
    classifier = DocumentClassifier()
    assert classifier.classify() == "Unknown"
    assert classifier.classify(document_type="Legislative Report") == "Unknown"
    assert classifier.classify(title="Letter to the Judge") == "Unknown"

def test_default_classifier():
    assert classify_document(document_type="Second Amended Complaint") == "Complaint"
