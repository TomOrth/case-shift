from unittest.mock import MagicMock

import pytest

from app.db.schema import init_schema


def test_init_schema_creates_indexes():
    mock_client = MagicMock()
    mock_graph = MagicMock()
    mock_client.select_graph.return_value = mock_graph

    init_schema(mock_client, "test_graph")

    mock_client.select_graph.assert_called_once_with("test_graph")

    expected_calls = [
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
    ]

    assert mock_graph.query.call_count == len(expected_calls)
    actual_calls = [call.args[0] for call in mock_graph.query.call_args_list]

    for expected in expected_calls:
        assert expected in actual_calls


def test_init_schema_handles_existing_indexes():
    mock_client = MagicMock()
    mock_graph = MagicMock()
    mock_client.select_graph.return_value = mock_graph

    def side_effect(*args, **kwargs):
        if "Case" in args[0]:
            raise Exception("Index already exists")
        return MagicMock()

    mock_graph.query.side_effect = side_effect

    init_schema(mock_client, "test_graph")

    assert mock_graph.query.call_count == 14


def test_init_schema_raises_on_unexpected_errors():
    mock_client = MagicMock()
    mock_graph = MagicMock()
    mock_client.select_graph.return_value = mock_graph

    def side_effect(*args, **kwargs):
        if "Case" in args[0]:
            raise Exception("Connection lost")
        return MagicMock()

    mock_graph.query.side_effect = side_effect

    with pytest.raises(RuntimeError) as exc_info:
        init_schema(mock_client, "test_graph")

    assert "Failed to create 1 index(es)" in str(exc_info.value)
    assert "Connection lost" in str(exc_info.value)
    assert mock_graph.query.call_count == 14
