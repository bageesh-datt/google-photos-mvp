import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

from unittest.mock import patch

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_groq_llm():
    with patch("backend.app.mvp.query_parser.extract_clues_llm", return_value=None):
        yield

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "online"

def test_photos_list_endpoint():
    res = client.get("/api/mvp/photos")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 50
    assert data[0]["photo_id"] == "P001"

def test_photo_detail_endpoint():
    res = client.get("/api/mvp/photos/P023")
    assert res.status_code == 200
    photo = res.json()
    assert photo["photo_id"] == "P023"
    assert photo["location"]["city"] == "Goa"

def test_search_endpoint():
    res = client.post("/api/mvp/search", json={"query": "family beach photo from Goa around 2022"})
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data
    assert len(data["results"]) > 0
    assert len(data["refinements"]) > 0

def test_refine_endpoint():
    # 1. Start search
    s_res = client.post("/api/mvp/search", json={"query": "family beach photo"})
    sid = s_res.json()["session_id"]
    
    # 2. Refine search
    r_res = client.post("/api/mvp/refine", json={
        "session_id": sid,
        "updated_clues": {"people": ["family"], "location": ["Goa"]}
    })
    assert r_res.status_code == 200
    r_data = r_res.json()
    assert r_data["attempt_number"] == 2

def test_confirm_endpoint():
    s_res = client.post("/api/mvp/search", json={"query": "family beach photo"})
    sid = s_res.json()["session_id"]
    
    c_res = client.post("/api/mvp/confirm", json={
        "session_id": sid,
        "selected_photo_id": "P023"
    })
    assert c_res.status_code == 200
    assert c_res.json()["status"] == "success"

def test_cold_start_first_search_request():
    """Regression test: verify that the VERY FIRST search request on fresh application startup succeeds."""
    import backend.app.mvp.embedding_service as emb_svc
    from backend.app.mvp.photo_store import PhotoStore
    emb_svc._MODEL_INSTANCE = None
    PhotoStore._instance = None
    
    with TestClient(app) as fresh_client:
        res = fresh_client.post("/api/mvp/search", json={"query": "lion"})
        assert res.status_code == 200
        data = res.json()
        assert "session_id" in data
        assert len(data["results"]) > 0
        assert data["results"][0]["photo_id"] in ["P038", "P005", "P003"]

def test_photos_route_redirect_and_assets():
    """Verify /photos and /photos/ redirect to / while static photo assets remain accessible."""
    no_redirect_client = TestClient(app, follow_redirects=False)
    
    # Check /photos
    r1 = no_redirect_client.get("/photos")
    assert r1.status_code in [307, 302, 301]
    assert r1.headers.get("location") == "/"
    
    # Check /photos/
    r2 = no_redirect_client.get("/photos/")
    assert r2.status_code in [307, 302, 301]
    assert r2.headers.get("location") == "/"
    
    # Check static asset serving for P001.jpg, P025.jpg, P050.jpg
    for pid in ["P001.jpg", "P025.jpg", "P050.jpg"]:
        img_res = no_redirect_client.get(f"/photos/{pid}")
        assert img_res.status_code == 200
        assert "image" in img_res.headers.get("content-type", "")



