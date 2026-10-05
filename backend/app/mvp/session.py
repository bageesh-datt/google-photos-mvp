import uuid
import time
from typing import Dict, Optional, List, Any
from backend.app.mvp.schemas import ParsedClues

class SearchSession:
    def __init__(self, session_id: str, initial_query: str, clues: ParsedClues):
        self.session_id = session_id
        self.initial_query = initial_query
        self.current_clues = clues
        self.attempt_number = 1
        self.created_at = time.time()
        self.updated_at = time.time()
        self.history: List[Dict[str, Any]] = []
        self.selected_photo_id: Optional[str] = None
        self.is_completed: bool = False
        
    def record_attempt(self, result_count: int, top_score: float, refinement_used: Optional[str] = None):
        self.history.append({
            "attempt": self.attempt_number,
            "timestamp": time.time(),
            "query": self.current_clues.raw_query,
            "clues": self.current_clues.model_dump(),
            "result_count": result_count,
            "top_score": top_score,
            "refinement_used": refinement_used
        })
        self.updated_at = time.time()

class SessionManager:
    _instance = None
    
    def __init__(self):
        self.sessions: Dict[str, SearchSession] = {}
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SessionManager()
        return cls._instance
        
    def create_session(self, initial_query: str, clues: ParsedClues) -> SearchSession:
        sid = f"sess_{uuid.uuid4().hex[:10]}"
        session = SearchSession(sid, initial_query, clues)
        self.sessions[sid] = session
        return session
        
    def get_session(self, session_id: str) -> Optional[SearchSession]:
        return self.sessions.get(session_id)
        
    def update_session_clues(self, session_id: str, new_clues: ParsedClues) -> Optional[SearchSession]:
        session = self.get_session(session_id)
        if session:
            session.current_clues = new_clues
            session.attempt_number += 1
            session.updated_at = time.time()
        return session
        
    def confirm_selection(self, session_id: str, photo_id: str) -> bool:
        session = self.get_session(session_id)
        if session:
            session.selected_photo_id = photo_id
            session.is_completed = True
            session.updated_at = time.time()
            return True
        return False

def get_session_manager() -> SessionManager:
    return SessionManager.get_instance()
