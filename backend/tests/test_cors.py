from fastapi.testclient import TestClient
from litigation_api.main import app

client = TestClient(app)

def test_cors_headers():
    # Test allowed origin
    origin = "http://localhost:3000"
    response = client.get(
        "/health",
        headers={"Origin": origin}
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin

def test_cors_preflight():
    # Test preflight request for allowed origin
    origin = "http://localhost:3000"
    response = client.options(
        "/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin
    assert "GET" in response.headers.get("access-control-allow-methods", "")

def test_cors_disallowed_origin():
    # Test disallowed origin
    origin = "http://malicious.com"
    response = client.get(
        "/health",
        headers={"Origin": origin}
    )
    assert response.status_code == 200
    # FastAPI's CORSMiddleware does not include the header if origin is not allowed
    assert "access-control-allow-origin" not in response.headers
