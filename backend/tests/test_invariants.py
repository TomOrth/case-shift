from fastapi.testclient import TestClient

from litigation_api.main import app
from litigation_api.models.domain import Case, Chunk, DocketEntry, Document
from litigation_api.db.schema import init_schema


def test_health_endpoint_contract_is_unversioned():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert client.get("/api/v1/health").status_code == 404


def test_tier1_domain_model_fields_are_spec_aligned():
    assert set(Case.model_fields) == {
        "case_id",
        "case_name",
        "court",
        "jurisdiction",
        "filed_date",
        "closed_date",
        "status",
    }
    assert set(DocketEntry.model_fields) == {
        "entry_id",
        "case_id",
        "docket_number",
        "filed_at",
        "title",
        "entry_type",
        "source_url",
    }
    assert set(Document.model_fields) == {
        "doc_id",
        "case_id",
        "entry_id",
        "document_type",
        "title",
        "filed_at",
        "author_type",
        "disposition",
        "summary",
        "summary_embedding",
    }
    assert set(Chunk.model_fields) == {
        "chunk_id",
        "doc_id",
        "case_id",
        "chunk_index",
        "page_start",
        "page_end",
        "text",
        "embedding",
    }


def test_schema_init_covers_required_lookup_path_indexes():
    queries = []

    class StubGraph:
        def query(self, query: str):
            queries.append(query)

    class StubClient:
        def select_graph(self, graph_name: str):
            return StubGraph()

    init_schema(StubClient(), "test_graph")

    expected_queries = {
        "CREATE INDEX FOR (n:Case) ON (n.case_id)",
        "CREATE INDEX FOR (n:DocketEntry) ON (n.entry_id)",
        "CREATE INDEX FOR (n:DocketEntry) ON (n.case_id)",
        "CREATE INDEX FOR (n:DocketEntry) ON (n.filed_at)",
        "CREATE INDEX FOR (n:Document) ON (n.doc_id)",
        "CREATE INDEX FOR (n:Document) ON (n.case_id)",
        "CREATE INDEX FOR (n:Document) ON (n.entry_id)",
        "CREATE INDEX FOR (n:Document) ON (n.filed_at)",
        "CREATE INDEX FOR (n:Chunk) ON (n.chunk_id)",
        "CREATE INDEX FOR (n:Chunk) ON (n.doc_id)",
        "CREATE INDEX FOR (n:Chunk) ON (n.case_id)",
        "CREATE INDEX FOR (n:Party) ON (n.party_id)",
        "CREATE INDEX FOR (n:Judge) ON (n.judge_id)",
        "CREATE INDEX FOR (n:EventType) ON (n.event_type_id)",
    }

    assert set(queries) == expected_queries
