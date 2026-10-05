import pytest
from backend.app.mvp.query_parser import parse_query
from backend.app.mvp.retrieval import execute_retrieval

def test_natural_language_query_preservation():
    raw = "an old photo where a man was wearing a black cap and working on a computer"
    clues = parse_query(raw)
    assert clues.raw_query == raw
    assert clues.semantic_query and len(clues.semantic_query) > 10
    # Stopwords and connector words MUST NOT enter ocr_text
    assert "photo" not in clues.ocr_text
    assert "written" not in clues.ocr_text
    assert "with" not in clues.ocr_text
    assert "on" not in clues.ocr_text
    assert "it" not in clues.ocr_text
    assert "computer" in clues.objects or "cap" in clues.clothing or "working" in clues.activities

def test_ocr_cleanliness_for_charity():
    raw = "photo with charity written on it"
    clues = parse_query(raw)
    assert clues.ocr_text == ["charity"]
    assert "photo" not in clues.ocr_text
    assert "written" not in clues.ocr_text
    assert "it" not in clues.ocr_text

def test_ocr_empty_for_people_standing_together():
    raw = "some people standing together inside a room"
    clues = parse_query(raw)
    assert clues.ocr_text == []
    assert clues.people_present is True
    assert clues.group_type == "group_of_people"
    assert "standing" in clues.spatial_relations or "together" in clues.spatial_relations
    assert clues.environment == "indoor"

def test_natural_search_beach_goa_sunset():
    raw = "a beach photo from Goa during sunset"
    clues = parse_query(raw)
    results, status = execute_retrieval(clues)
    assert status in ["strong_matches", "weak_matches"]
    assert len(results) > 0
    top_pids = [r.photo_id for r in results[:5]]
    # Must retrieve Goa beach photos (P011, P013, P015, P019, P023)
    assert any(pid in top_pids for pid in ["P011", "P013", "P015", "P019", "P023"])

def test_natural_search_smg_hat():
    raw = "the picture where SMG was written on the hat"
    clues = parse_query(raw)
    results, status = execute_retrieval(clues)
    assert status in ["strong_matches", "weak_matches"]
    assert len(results) > 0
    # P001 has SMG written on hat
    assert results[0].photo_id == "P001"

def test_natural_search_lion_green_area():
    raw = "a lion in a green area"
    clues = parse_query(raw)
    results, status = execute_retrieval(clues)
    assert status in ["strong_matches", "weak_matches"]
    assert len(results) > 0
    top_pids = [r.photo_id for r in results[:3]]
    assert "P038" in top_pids or "P003" in top_pids

def test_natural_search_birthday_cake():
    raw = "people celebrating a birthday with cake"
    clues = parse_query(raw)
    results, status = execute_retrieval(clues)
    assert status in ["strong_matches", "weak_matches"]
    assert len(results) > 0
    top_pids = [r.photo_id for r in results[:5]]
    assert any(pid in top_pids for pid in ["P012", "P021", "P022", "P026", "P028"])

def test_natural_search_dog_outdoors():
    raw = "dog running outdoors"
    clues = parse_query(raw)
    results, status = execute_retrieval(clues)
    assert status in ["strong_matches", "weak_matches"]
    assert len(results) > 0
    top_pids = [r.photo_id for r in results[:3]]
    assert "P037" in top_pids

def test_natural_search_people_around_table():
    raw = "people sitting around a table"
    clues = parse_query(raw)
    results, status = execute_retrieval(clues)
    assert status in ["strong_matches", "weak_matches"]
    assert len(results) > 0
    top_pids = [r.photo_id for r in results[:5]]
    assert any(pid in top_pids for pid in ["P022", "P027", "P040", "P047", "P048"])

def test_natural_search_no_match():
    raw = "astronaut walking on the moon with a giant space shuttle"
    clues = parse_query(raw)
    results, status = execute_retrieval(clues)
    assert status in ["zero_matches", "weak_matches"] or len(results) == 0 or results[0].score <= 0.35

