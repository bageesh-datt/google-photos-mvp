from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class DateRange(BaseModel):
    start: Optional[str] = None  # YYYY-MM-DD
    end: Optional[str] = None    # YYYY-MM-DD

class ConfidenceScores(BaseModel):
    date: str = "medium"
    location: str = "medium"
    people: str = "medium"
    event: str = "medium"
    objects: str = "medium"

class PeopleSemantics(BaseModel):
    present: bool = False
    count: int = 0
    count_bucket: str = "none"  # "none", "one", "two", "small_group", "medium_group", "large_group", "crowd"
    group_type: str = "none"    # "none", "individual", "couple", "group_of_people", "family_group", "crowd"
    people_context: str = ""    # e.g., "multiple people standing together", "crowd at festival"
    relationships: List[str] = Field(default_factory=list)

class ParsedClues(BaseModel):
    raw_query: str
    semantic_query: Optional[str] = None
    approximate_date: Optional[str] = None
    date_range: Optional[DateRange] = None
    people: List[str] = Field(default_factory=list)
    people_present: Optional[bool] = None
    people_count: Optional[int] = None
    people_count_bucket: Optional[str] = None  # "none", "one", "two", "small_group", "medium_group", "large_group", "crowd"
    group_type: Optional[str] = None           # "individual", "couple", "group_of_people", "family_group", "crowd"
    people_context: Optional[str] = None
    spatial_relations: List[str] = Field(default_factory=list)
    location: List[str] = Field(default_factory=list)
    event: List[str] = Field(default_factory=list)
    objects: List[str] = Field(default_factory=list)
    animals: List[str] = Field(default_factory=list)
    clothing: List[str] = Field(default_factory=list)
    colors: List[str] = Field(default_factory=list)
    activities: List[str] = Field(default_factory=list)
    environment: Optional[str] = None
    visual_concepts: List[str] = Field(default_factory=list)
    ocr_text: List[str] = Field(default_factory=list)
    confidence: ConfidenceScores = Field(default_factory=ConfidenceScores)
    is_fallback: bool = False

class PhotoLocation(BaseModel):
    city: str
    state: Optional[str] = ""
    country: str
    landmark: Optional[str] = ""

class VisualSemantics(BaseModel):
    objects: List[str] = Field(default_factory=list)
    animals: List[str] = Field(default_factory=list)
    people: PeopleSemantics = Field(default_factory=PeopleSemantics)
    activities: List[str] = Field(default_factory=list)
    scene: str = ""
    environment: str = ""  # e.g., "indoor", "outdoor", "daytime", "night"
    clothing: List[str] = Field(default_factory=list)
    colors: List[str] = Field(default_factory=list)
    spatial_relations: List[str] = Field(default_factory=list)
    visual_concepts: List[str] = Field(default_factory=list)
    people_context: str = ""
    generated_description: str = ""
    visual_embedding: Optional[List[float]] = None  # Vector embedding

class PhotoRecord(BaseModel):
    photo_id: str
    filename: str
    image_url: str
    date: str
    year: int
    month: Optional[int] = 1
    season: Optional[str] = ""
    location: PhotoLocation
    people: List[str] = Field(default_factory=list)
    people_relationships: List[str] = Field(default_factory=list)
    event: str
    objects: List[str] = Field(default_factory=list)
    visual_concepts: List[str] = Field(default_factory=list)
    visual_semantics: Optional[VisualSemantics] = None
    ocr_text: Optional[str] = ""
    album: str
    is_favorite: bool = False
    description: str = ""

class RankedResult(BaseModel):
    photo_id: str
    filename: str
    image_url: str
    date: str
    year: int
    location: str
    event: str
    album: str
    score: float
    sub_scores: Dict[str, float] = Field(default_factory=dict)
    match_reasons: List[str] = Field(default_factory=list)
    is_favorite: bool = False
    description: str = ""
    people: List[str] = Field(default_factory=list)
    objects: List[str] = Field(default_factory=list)
    visual_semantics: Optional[VisualSemantics] = None
    ocr_text: str = ""


class RefinementOption(BaseModel):
    id: str
    label: str
    action_type: str  # e.g., "broaden_date", "add_person", "try_ocr", "toggle_clue", "custom"
    description: str
    payload: Dict[str, Any] = Field(default_factory=dict)

class SearchRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class RefinementRequest(BaseModel):
    session_id: str
    action_id: Optional[str] = None
    updated_clues: Optional[Dict[str, Any]] = None

class ConfirmRequest(BaseModel):
    session_id: str
    selected_photo_id: str

class SearchResponse(BaseModel):
    session_id: str
    attempt_number: int
    raw_query: str
    clues: ParsedClues
    results: List[RankedResult]
    total_candidates: int
    result_status: str  # "strong_matches", "weak_matches", "zero_matches"
    refinements: List[RefinementOption]
