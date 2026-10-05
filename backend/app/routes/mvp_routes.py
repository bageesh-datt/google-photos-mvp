from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any

from backend.app.mvp.schemas import (
    SearchRequest, SearchResponse, RefinementRequest, ConfirmRequest,
    PhotoRecord, RankedResult, ParsedClues
)
from backend.app.mvp.query_parser import parse_query
from backend.app.mvp.retrieval import execute_retrieval
from backend.app.mvp.refinement import generate_refinement_options, apply_refinement_to_clues
from backend.app.mvp.session import get_session_manager
from backend.app.mvp.photo_store import get_photo_store

router = APIRouter(prefix="/api/mvp", tags=["MVP Photo Search"])

@router.post("/search", response_model=SearchResponse)
def search_photos(req: SearchRequest):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")
        
    session_mgr = get_session_manager()
    
    # Check if session exists or parse new query
    if req.session_id and session_mgr.get_session(req.session_id):
        session = session_mgr.get_session(req.session_id)
        clues = parse_query(req.query)
        session_mgr.update_session_clues(session.session_id, clues)
    else:
        clues = parse_query(req.query)
        session = session_mgr.create_session(req.query, clues)
        
    results, status = execute_retrieval(clues)
    refinements = generate_refinement_options(clues, results, status)
    
    top_score = results[0].score if results else 0.0
    session.record_attempt(result_count=len(results), top_score=top_score)
    
    return SearchResponse(
        session_id=session.session_id,
        attempt_number=session.attempt_number,
        raw_query=req.query,
        clues=clues,
        results=results,
        total_candidates=len(results),
        result_status=status,
        refinements=refinements
    )

@router.post("/refine", response_model=SearchResponse)
def refine_photos(req: RefinementRequest):
    session_mgr = get_session_manager()
    session = session_mgr.get_session(req.session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail=f"Search session '{req.session_id}' not found.")
        
    current_clues = session.current_clues
    
    # Apply updated clues if provided directly or via payload
    if req.updated_clues:
        new_clues = current_clues.model_copy(deep=True)
        if "approximate_date" in req.updated_clues:
            new_clues.approximate_date = req.updated_clues["approximate_date"]
        if "people" in req.updated_clues and isinstance(req.updated_clues["people"], list):
            new_clues.people = req.updated_clues["people"]
        if "location" in req.updated_clues and isinstance(req.updated_clues["location"], list):
            new_clues.location = req.updated_clues["location"]
        if "event" in req.updated_clues and isinstance(req.updated_clues["event"], list):
            new_clues.event = req.updated_clues["event"]
        if "objects" in req.updated_clues and isinstance(req.updated_clues["objects"], list):
            new_clues.objects = req.updated_clues["objects"]
        if "ocr_text" in req.updated_clues and isinstance(req.updated_clues["ocr_text"], list):
            new_clues.ocr_text = req.updated_clues["ocr_text"]
        clues = new_clues
    else:
        clues = current_clues
        
    session_mgr.update_session_clues(session.session_id, clues)
    
    results, status = execute_retrieval(clues)
    refinements = generate_refinement_options(clues, results, status)
    
    top_score = results[0].score if results else 0.0
    session.record_attempt(result_count=len(results), top_score=top_score, refinement_used=req.action_id)
    
    return SearchResponse(
        session_id=session.session_id,
        attempt_number=session.attempt_number,
        raw_query=session.initial_query,
        clues=clues,
        results=results,
        total_candidates=len(results),
        result_status=status,
        refinements=refinements
    )

@router.get("/photos", response_model=List[PhotoRecord])
def get_all_photos():
    store = get_photo_store()
    return store.get_all_photos()

@router.get("/photos/{photo_id}", response_model=PhotoRecord)
def get_photo(photo_id: str):
    store = get_photo_store()
    photo = store.get_photo_by_id(photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail=f"Photo ID '{photo_id}' not found.")
    return photo

@router.post("/confirm")
def confirm_photo(req: ConfirmRequest):
    session_mgr = get_session_manager()
    success = session_mgr.confirm_selection(req.session_id, req.selected_photo_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Session ID '{req.session_id}' not found.")
    return {"status": "success", "session_id": req.session_id, "confirmed_photo_id": req.selected_photo_id}
