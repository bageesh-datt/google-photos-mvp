import re
from typing import List, Dict, Any
from backend.app.mvp.schemas import ParsedClues, RankedResult, RefinementOption, DateRange

def generate_refinement_options(clues: ParsedClues, results: List[RankedResult], result_status: str) -> List[RefinementOption]:
    options: List[RefinementOption] = []
    
    # 1. Date Broadening
    if clues.approximate_date:
        try:
            yr = int(clues.approximate_date)
            broader_label = f"Broaden date range to {yr-1}–{yr+1}"
            options.append(RefinementOption(
                id="ref_broaden_date",
                label=broader_label,
                action_type="broaden_date",
                description="Expand search window by 1 year before and after",
                payload={"field": "date_range", "start": f"{yr-1}-01-01", "end": f"{yr+1}-12-31"}
            ))
        except Exception:
            pass
    elif not clues.approximate_date and not clues.date_range:
        options.append(RefinementOption(
            id="ref_add_year",
            label="Filter by Year (e.g., 2022 or 2023)",
            action_type="add_year",
            description="Add an approximate year clue to narrow down timeline",
            payload={"field": "approximate_date", "value": "2022"}
        ))
        
    # 2. People refinement
    if not clues.people:
        options.append(RefinementOption(
            id="ref_add_family",
            label="Add 'Family' context clue",
            action_type="add_people",
            description="Filter results for family gatherings and relatives",
            payload={"field": "people", "value": "family"}
        ))
        options.append(RefinementOption(
            id="ref_add_friends",
            label="Add 'Friends' context clue",
            action_type="add_people",
            description="Filter results for friends trips and outings",
            payload={"field": "people", "value": "friends"}
        ))
    elif "family" in [p.lower() for p in clues.people]:
        options.append(RefinementOption(
            id="ref_switch_friends",
            label="Switch clue from Family to Friends",
            action_type="update_people",
            description="Look for college/bachelor friends photos instead",
            payload={"field": "people", "value": "friends"}
        ))
        
    # 3. Location / Place refinement
    if not clues.location:
        options.append(RefinementOption(
            id="ref_add_goa",
            label="Try location clue 'Goa' or 'Beach'",
            action_type="add_location",
            description="Filter by coastal beach trip destinations",
            payload={"field": "location", "value": "Goa"}
        ))
        options.append(RefinementOption(
            id="ref_add_mountains",
            label="Try location clue 'Manali' or 'Mountains'",
            action_type="add_location",
            description="Filter by hill station mountain retreats",
            payload={"field": "location", "value": "Manali"}
        ))
        
    # 4. OCR / Text search refinement
    if not clues.ocr_text:
        options.append(RefinementOption(
            id="ref_try_ocr",
            label="Search for visible text in documents/bills",
            action_type="try_ocr",
            description="Surface passports, electricity bills, or flight tickets",
            payload={"field": "ocr_text", "value": "passport bill certificate"}
        ))
        
    # 5. Remove restrictive clue if present
    if clues.location and len(clues.location) > 0:
        loc_str = clues.location[0].title()
        options.append(RefinementOption(
            id="ref_remove_location",
            label=f"Remove place filter '{loc_str}'",
            action_type="remove_clue",
            description=f"Broaden search beyond {loc_str}",
            payload={"field": "remove_location", "value": clues.location[0]}
        ))
        
    return options[:4]  # Return top 4 most relevant actionable recovery cards

def apply_refinement_to_clues(clues: ParsedClues, payload: Dict[str, Any]) -> ParsedClues:
    field = payload.get("field")
    val = payload.get("value")
    
    new_clues = clues.model_copy(deep=True)
    
    if field == "date_range":
        new_clues.date_range = DateRange(start=payload.get("start"), end=payload.get("end"))
        new_clues.approximate_date = f"{payload.get('start', '')[:4]}-{payload.get('end', '')[:4]}"
    elif field == "approximate_date":
        new_clues.approximate_date = str(val)
        new_clues.date_range = DateRange(start=f"{val}-01-01", end=f"{val}-12-31")
    elif field == "people":
        if val not in new_clues.people:
            new_clues.people.append(str(val))
    elif field == "location":
        if val not in new_clues.location:
            new_clues.location.append(str(val))
    elif field == "ocr_text":
        new_clues.ocr_text.extend(str(val).split())
    elif field == "remove_location":
        rem = payload.get("value")
        new_clues.location = [l for l in new_clues.location if l.lower() != str(rem).lower()]
        
    return new_clues
