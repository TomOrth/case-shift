from unittest.mock import MagicMock, patch

from app.scripts.init_db import _redact_url, main


def test_redact_url_removes_credentials():
    redacted = _redact_url("redis://user:secret@example.com:6379/0")
    assert redacted == "redis://example.com:6379/0"


@patch("app.scripts.init_db.init_schema")
@patch("app.scripts.init_db.FalkorDB")
def test_main_passes_configured_graph_name(mock_falkordb, mock_init_schema):
    mock_client = MagicMock()
    mock_falkordb.from_url.return_value = mock_client

    with patch("app.scripts.init_db.settings") as mock_settings:
        mock_settings.falkordb_url = "redis://localhost:6379/0"
        mock_settings.falkordb_graph_name = "custom_graph"
        main()

    mock_falkordb.from_url.assert_called_once_with("redis://localhost:6379/0")
    mock_init_schema.assert_called_once_with(mock_client, "custom_graph")
