import pytest
from unittest.mock import patch
from backend.app.mvp.query_parser import parse_query
from backend.app.mvp.retrieval import execute_retrieval
from backend.app.mvp.refinement import generate_refinement_options, apply_refinement_to_clues

@pytest.fixture(autouse=True)
def mock_groq():
    with patch("backend.app.mvp.query_parser.extract_clues_llm", return_value=None):
        yield

def test_generate_refinements():
    clues = parse_query("beach photo 2022")
    results, status = execute_retrieval(clues)
    refinements = generate_refinement_options(clues, results, status)
    
    assert len(refinements) > 0
    assert any("broaden" in r.label.lower() or "year" in r.label.lower() for r in refinements)

def test_apply_refinement():
    clues = parse_query("beach photo 2022")
    payload = {"field": "people", "value": "family"}
    updated = apply_refinement_to_clues(clues, payload)
    
    assert "family" in updated.people
