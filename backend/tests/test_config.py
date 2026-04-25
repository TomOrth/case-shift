from litigation_api.core.config import Settings


def test_settings_default_values():
    settings = Settings()
    assert settings.app_name == "case-shift-backend"
    assert settings.environment == "development"
    assert settings.debug is True
    assert settings.redis_url == "redis://localhost:6379/0"
    assert settings.falkordb_url == "redis://localhost:6379"
    assert settings.falkordb_graph_name == "case_shift"
    assert settings.s3_endpoint_url == "http://localhost:4566"
    assert settings.s3_bucket_name == "case-shift-artifacts"
