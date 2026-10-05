import pytest
from backend.app.mvp.query_parser import parse_query, fallback_parse_query

def test_fallback_parse_year_and_place():
    query = "family beach photo from Goa around 2022"
    clues = fallback_parse_query(query)
    
    assert clues.approximate_date == "2022"
    assert clues.date_range is not None
    assert clues.date_range.start == "2022-01-01"
    assert "goa" in [l.lower() for l in clues.location]
    assert "beach" in [l.lower() for l in clues.location] or "beach" in [o.lower() for o in clues.objects]
    assert "family" in [p.lower() for p in clues.people]

def test_fallback_parse_birthday_event():
    query = "birthday photo with my cousin Rohan"
    clues = fallback_parse_query(query)
    
    assert "birthday" in [e.lower() for e in clues.event]
    assert any(p.lower() in ["rohan", "cousin", "cousins"] for p in clues.people)

def test_fallback_parse_document_ocr():
    query = "document where passport text is visible"
    clues = fallback_parse_query(query)
    
    assert "passport" in [o.lower() for o in clues.ocr_text] or "passport" in [o.lower() for o in clues.objects]

def test_arbitrary_single_clue_query():
    query = "pizza"
    with patch("backend.app.mvp.groq_client.extract_clues_llm", return_value=None):
        clues = parse_query(query)
    assert clues.raw_query == "pizza"
    assert len(clues.raw_query) > 0

def test_empty_query():
    clues = parse_query("")
    assert clues.raw_query == ""

def test_natural_language_color_hat_smg():
    query = "a black and white color hat written on smg"
    clues = parse_query(query)
    assert clues.ocr_text == ["smg"]
    assert "hat" not in clues.ocr_text
    assert "black" in clues.colors
    assert "white" in clues.colors
    assert "hat" in clues.clothing or "hat" in clues.objects
    assert "written" not in clues.ocr_text
    assert "color" not in clues.ocr_text

def test_natural_language_additional_patterns():
    c1 = parse_query("a black hat with SMG written on it")
    assert c1.ocr_text == ["smg"]
    assert "hat" not in c1.ocr_text
    assert "black" in c1.colors
    assert "hat" in c1.clothing or "hat" in c1.objects

    c2 = parse_query("a white cap with ABC written on it")
    assert c2.ocr_text == ["abc"]
    assert "cap" not in c2.ocr_text
    assert "white" in c2.colors

    c3 = parse_query("a red shirt with Nike written on it")
    assert c3.ocr_text == ["nike"]
    assert "shirt" not in c3.ocr_text
    assert "red" in c3.colors

    c4 = parse_query("people standing together")
    assert c4.ocr_text == []
    assert c4.people_present is True
    assert "standing" in c4.spatial_relations or "together" in c4.spatial_relations

    c5 = parse_query("lion in a green area")
    assert c5.ocr_text == []
    assert "lion" in c5.animals or "lion" in c5.objects
    assert "green" in c5.colors

# --- Groq Resilience & Rate Limit Tests ---
from unittest.mock import MagicMock, patch
import json
from groq import RateLimitError

def test_groq_primary_success(monkeypatch):
    monkeypatch.setattr("backend.app.config.settings.GROQ_API_KEY", "test_key_secret_123")
    monkeypatch.setattr("backend.app.config.settings.GROQ_MODEL", "model-primary")
    monkeypatch.setattr("backend.app.config.settings.GROQ_FALLBACK_MODEL", "model-fallback")
    
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps({"objects": ["lion"], "visual_concepts": ["lion"]})
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    mock_groq = MagicMock()
    mock_groq.chat.completions.create.return_value = mock_response
    
    with patch("groq.Groq", return_value=mock_groq):
        from backend.app.mvp.groq_client import extract_clues_llm
        result = extract_clues_llm("lion")
        assert result == {"objects": ["lion"], "visual_concepts": ["lion"]}
        mock_groq.chat.completions.create.assert_called_once()
        assert mock_groq.chat.completions.create.call_args[1]["model"] == "model-primary"

def test_groq_primary_429_fallback_success(monkeypatch):
    monkeypatch.setattr("backend.app.config.settings.GROQ_API_KEY", "test_key_secret_123")
    monkeypatch.setattr("backend.app.config.settings.GROQ_MODEL", "model-primary")
    monkeypatch.setattr("backend.app.config.settings.GROQ_FALLBACK_MODEL", "model-fallback")
    
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps({"location": ["goa"]})
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    mock_groq = MagicMock()
    mock_groq.chat.completions.create.side_effect = [
        RateLimitError(message="429 Rate limit", response=MagicMock(status_code=429), body={}),
        mock_response
    ]
    
    with patch("groq.Groq", return_value=mock_groq):
        from backend.app.mvp.groq_client import extract_clues_llm
        result = extract_clues_llm("goa")
        assert result == {"location": ["goa"]}
        assert mock_groq.chat.completions.create.call_count == 2
        calls = mock_groq.chat.completions.create.call_args_list
        assert calls[0][1]["model"] == "model-primary"
        assert calls[1][1]["model"] == "model-fallback"

def test_groq_primary_and_fallback_failure_uses_deterministic(monkeypatch):
    monkeypatch.setattr("backend.app.config.settings.GROQ_API_KEY", "test_key_secret_123")
    monkeypatch.setattr("backend.app.config.settings.GROQ_MODEL", "model-primary")
    monkeypatch.setattr("backend.app.config.settings.GROQ_FALLBACK_MODEL", "model-fallback")
    
    mock_groq = MagicMock()
    mock_groq.chat.completions.create.side_effect = [
        RateLimitError(message="429 Rate limit", response=MagicMock(status_code=429), body={}),
        Exception("500 Internal Error")
    ]
    
    with patch("groq.Groq", return_value=mock_groq):
        clues = parse_query("lion")
        assert clues.is_fallback is True
        assert "lion" in clues.objects

def test_groq_no_fallback_configured(monkeypatch):
    monkeypatch.setattr("backend.app.config.settings.GROQ_API_KEY", "test_key_secret_123")
    monkeypatch.setattr("backend.app.config.settings.GROQ_MODEL", "model-primary")
    monkeypatch.setattr("backend.app.config.settings.GROQ_FALLBACK_MODEL", "")
    monkeypatch.setattr("backend.app.config.settings.GROQ_FALLBACK_MODELS", "")
    
    mock_groq = MagicMock()
    mock_groq.chat.completions.create.side_effect = RateLimitError(message="429 Rate limit", response=MagicMock(status_code=429), body={})
    
    with patch("groq.Groq", return_value=mock_groq):
        from backend.app.mvp.groq_client import extract_clues_llm
        result = extract_clues_llm("lion")
        assert result is None
        assert mock_groq.chat.completions.create.call_count == 1

def test_groq_api_key_missing(monkeypatch):
    monkeypatch.setattr("backend.app.config.settings.GROQ_API_KEY", "")
    
    with patch("groq.Groq") as mock_groq_cls:
        from backend.app.mvp.groq_client import extract_clues_llm
        result = extract_clues_llm("lion")
        assert result is None
        mock_groq_cls.assert_not_called()

def test_groq_malformed_llm_json(monkeypatch):
    monkeypatch.setattr("backend.app.config.settings.GROQ_API_KEY", "test_key_secret_123")
    monkeypatch.setattr("backend.app.config.settings.GROQ_MODEL", "model-primary")
    monkeypatch.setattr("backend.app.config.settings.GROQ_FALLBACK_MODEL", "")
    
    mock_choice = MagicMock()
    mock_choice.message.content = "Not a JSON document"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    mock_groq = MagicMock()
    mock_groq.chat.completions.create.return_value = mock_response
    
    with patch("groq.Groq", return_value=mock_groq):
        clues = parse_query("lion")
        assert clues.is_fallback is True
        assert "lion" in clues.objects

def test_no_api_key_leakage_in_logs(monkeypatch, caplog):
    secret_key = "super_secret_groq_key_99999"
    monkeypatch.setattr("backend.app.config.settings.GROQ_API_KEY", secret_key)
    monkeypatch.setattr("backend.app.config.settings.GROQ_MODEL", "model-primary")
    monkeypatch.setattr("backend.app.config.settings.GROQ_FALLBACK_MODEL", "model-fallback")
    
    mock_groq = MagicMock()
    mock_groq.chat.completions.create.side_effect = RateLimitError(message=f"Rate limit error with info", response=MagicMock(status_code=429), body={})
    
    with caplog.at_level("WARNING"):
        with patch("groq.Groq", return_value=mock_groq):
            from backend.app.mvp.groq_client import extract_clues_llm
            extract_clues_llm("beach")
            
    log_text = caplog.text
    assert secret_key not in log_text

