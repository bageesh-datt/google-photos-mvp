import re
import logging
from typing import Dict, Any, List, Optional
from backend.app.mvp.schemas import ParsedClues, DateRange, ConfidenceScores
from backend.app.mvp.groq_client import extract_clues_llm

logger = logging.getLogger(__name__)

# Taxonomies for deterministic fallback parser
LOCATION_KEYWORDS = {
    "goa", "delhi", "new delhi", "mumbai", "pune", "jaipur", "mathura", "bengaluru", "bangalore",
    "ahmedabad", "manali", "udaipur", "shimla", "kochi", "alleppey", "agra", "hyderabad", "kolkata",
    "mysuru", "mysore", "srinagar", "gulmarg", "rishikesh", "beach", "lake", "fort", "waterfall",
    "mountain", "park", "restaurant", "cafe", "airport", "temple", "church", "pandal", "promenade"
}

PEOPLE_KEYWORDS = {
    "family", "mom", "dad", "mother", "father", "dadi", "grandma", "grandpa", "cousin", "cousins",
    "friend", "friends", "brother", "sister", "kids", "children", "parents", "relatives", "colleagues",
    "team", "aarav", "meera", "rohan", "sneha", "vikram", "kabir", "ananya", "priya", "rahul"
}

EVENT_KEYWORDS = {
    "diwali", "holi", "christmas", "uttarayan", "raksha bandhan", "rakhi", "vacation", "trip",
    "trek", "hike", "birthday", "bday", "wedding", "sangeet", "anniversary", "party", "reunion",
    "dinner", "lunch", "festival", "dasara", "onam", "puja", "pujas", "rafting", "skiing"
}

OBJECT_NOUNS = {
    "hat", "cap", "shirt", "t-shirt", "tshirt", "gown", "dress", "jacket", "hoodie", "coat", "saree", "pants", "shoes",
    "mug", "cup", "cake", "burger", "pizza", "biryani", "beer", "tea", "chai", "coffee", "passport", "bill", "ticket",
    "boarding pass", "certificate", "agreement", "smartcard", "card", "paper", "sign", "board", "banner", "wall",
    "document", "receipt", "building", "car", "vehicle", "truck", "boat", "house", "tree", "table", "chair", "desk",
    "laptop", "computer", "phone", "mobile", "flag", "box", "bottle", "can", "jar", "frisbee", "racket", "bike",
    "bicycle", "kites", "snow", "waterfall", "beach", "flower", "flowers", "light", "lights", "lion", "dog", "retriever", "cat", "bird", "gondola", "skis", "tulips", "fountain"
}

OBJECT_KEYWORDS = OBJECT_NOUNS.union({
    "diyas", "rangoli", "houseboat"
})

ANIMAL_KEYWORDS = {"lion", "dog", "retriever", "cat", "bird", "horse", "tiger", "asiatic lion"}

CLOTHING_KEYWORDS = {
    "cap", "black cap", "white cap", "hat", "black hat", "white hat", "shirt", "red shirt", "t-shirt", "tshirt",
    "gown", "dress", "black dress", "jacket", "hoodie", "coat", "saree", "umbrella", "goggles", "helmet"
}

COLOR_KEYWORDS = {
    "black", "white", "red", "yellow", "blue", "green", "pink", "purple", "orange", "brown", "grey", "gray", "golden", "gold", "silver", "amber"
}

DESCRIPTORS = {"color", "colors", "colored", "coloured"}

ACTIVITY_KEYWORDS = {
    "working", "work", "celebrating", "celebrate", "running", "run", "standing", "stand", "sitting", "sit",
    "hiking", "hike", "skiing", "ski", "rafting", "raft", "cycling", "cycle", "dancing", "dance",
    "walking", "walk", "eating", "eat", "flying", "fly", "stroll", "safari", "tasting", "tour", "posing", "pose"
}

STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "from", "to", "of", "for", "with", "by", "about", "around",
    "photo", "photos", "pic", "pics", "picture", "pictures", "image", "images", "some", "my",
    "me", "show", "find", "get", "look", "looking", "search", "see", "taken", "shot", "view",
    "where", "is", "are", "was", "were", "this", "that", "these", "those", "it", "there", "here",
    "when", "what", "which", "who", "whom", "whose", "why", "how", "has", "have", "had", "be",
    "been", "being", "do", "does", "did", "can", "could", "would", "should", "shall", "will",
    "another", "other", "any", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "just", "into", "during", "before", "after", "above", "below", "between", "up", "down", "out", "off", "over", "under", "and"
}

NON_OCR_WORDS = STOP_WORDS.union({
    "written", "printed", "text", "says", "reading", "label", "signed", "saying", "reads", "say",
    "photo", "photos", "pic", "pics", "picture", "pictures", "image", "images", "with", "on", "in", "at",
    "it", "this", "that", "there", "here", "where", "standing", "sitting", "together", "room", "inside",
    "outside", "indoor", "outdoor", "people", "man", "woman", "men", "women", "boy", "girl", "person",
    "area", "wearing", "working", "celebrating", "running", "some", "from", "during", "sunset", "beach",
    "lake", "mountain", "park"
}).union(OBJECT_NOUNS).union(COLOR_KEYWORDS).union(DESCRIPTORS)

def extract_clean_ocr_text(raw_query: str, raw_ocr_candidates: List[str]) -> List[str]:
    q_lower = raw_query.lower().strip()
    clean_ocr = []
    
    def is_valid_ocr(token: str) -> bool:
        t = token.lower().strip()
        if not t or t in NON_OCR_WORDS or re.match(r'^(19|20)\d{2}$', t):
            return False
        return True

    # 1. Explicit text intent keywords
    has_text_intent = any(k in q_lower for k in ["written", "text", "printed", "says", "reading", "label", "signed", "saying", "reads", "sign"])
    
    # Extract uppercase/acronym tokens (e.g. SMG, ABC, BESCOM, COWIN)
    caps_tokens = re.findall(r'\b[A-Z0-9]{2,}\b', raw_query)
    for cap in caps_tokens:
        c_l = cap.lower()
        if is_valid_ocr(c_l) and c_l not in clean_ocr:
            clean_ocr.append(c_l)

    if has_text_intent:
        # Pattern: "X written on Y" -> X is target text
        w_match_before = re.search(r'\b([a-z0-9]+)\s+(?:written|printed|text|labeled|signed|says|reading)\b', q_lower)
        if w_match_before:
            term = w_match_before.group(1)
            if is_valid_ocr(term) and term not in clean_ocr:
                clean_ocr.append(term)
                
        # Pattern: "written/text/says X" or "written on X" or "written in X"
        w_match_after = re.search(r'\b(?:written|printed|text|reading|says|saying|label|reads|sign)\s+(?:on|in|saying|say|reads)?\s*([a-z0-9]+)\b', q_lower)
        if w_match_after:
            term = w_match_after.group(1)
            if is_valid_ocr(term) and term not in clean_ocr:
                clean_ocr.append(term)
                
    # Add LLM output OCR items if strictly valid non-connector terms
    for candidate in raw_ocr_candidates:
        c_clean = candidate.lower().strip()
        if is_valid_ocr(c_clean) and c_clean not in clean_ocr:
            words_count = len(re.findall(r'\b[a-z0-9]+\b', q_lower))
            if has_text_intent or caps_tokens or words_count <= 2:
                clean_ocr.append(c_clean)
                
    # Standalone 1-word search term that isn't a stopword (e.g. "charity", "smg")
    words_in_query = [w for w in re.findall(r'\b[a-z0-9]+\b', q_lower) if w not in STOP_WORDS]
    if len(words_in_query) == 1:
        w_solo = words_in_query[0]
        if is_valid_ocr(w_solo) and w_solo not in clean_ocr:
            clean_ocr.append(w_solo)

    return clean_ocr

def fallback_parse_query(raw_query: str) -> ParsedClues:
    q_lower = raw_query.lower().strip()
    
    # 1. Date extraction
    approx_date = None
    date_range = None
    
    year_match = re.search(r'\b(20\d{2}|19\d{2})\b', q_lower)
    if year_match:
        found_year = year_match.group(1)
        approx_date = found_year
        date_range = DateRange(start=f"{found_year}-01-01", end=f"{found_year}-12-31")
    elif "recent" in q_lower or "this year" in q_lower:
        approx_date = "2023"
        date_range = DateRange(start="2023-01-01", end="2023-12-31")
    elif "2 years ago" in q_lower or "around 2021" in q_lower:
        approx_date = "2021"
        date_range = DateRange(start="2021-01-01", end="2021-12-31")
        
    # 2. Taxonomy extractions
    found_locations = [kw for kw in LOCATION_KEYWORDS if kw in q_lower]
    found_people = [kw for kw in PEOPLE_KEYWORDS if kw in q_lower]
    found_events = [kw for kw in EVENT_KEYWORDS if kw in q_lower]
    found_objects = [kw for kw in OBJECT_KEYWORDS if kw in q_lower]
    found_animals = [kw for kw in ANIMAL_KEYWORDS if kw in q_lower]
    found_clothing = [kw for kw in CLOTHING_KEYWORDS if kw in q_lower]
    found_colors = [kw for kw in COLOR_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', q_lower)]
    found_activities = [kw for kw in ACTIVITY_KEYWORDS if kw in q_lower]

    # Environment
    env = None
    if any(k in q_lower for k in ["indoor", "room", "office", "cafeteria", "living room", "home", "house", "table"]):
        env = "indoor"
    elif any(k in q_lower for k in ["outdoor", "beach", "mountain", "park", "jungle", "garden", "green area", "lawn", "river"]):
        env = "outdoor"

    # Clean OCR extraction
    found_ocr = extract_clean_ocr_text(raw_query, [])
    
    # 3. Generic token extraction for unlisted terms
    words = [w for w in re.findall(r'\b[a-z0-9]+\b', q_lower) if w not in STOP_WORDS and not re.match(r'^(19|20)\d{2}$', w)]
    
    # Unrecognized non-stop words become generic visual concepts
    unmatched_tokens = []
    known_matched_tokens = set(found_locations + found_people + found_events + found_objects + found_animals + found_clothing + found_colors + found_activities + found_ocr)
    for word in words:
        if word not in NON_OCR_WORDS and not any(word in matched for matched in known_matched_tokens):
            unmatched_tokens.append(word)
            
    if unmatched_tokens:
        found_objects = list(set(found_objects + unmatched_tokens))
    
    visual_concepts = list(set(found_locations + found_objects + found_animals + found_clothing + found_colors + found_activities + unmatched_tokens))
    
    # People group intent & spatial relation extraction
    people_present = None
    people_count_bucket = None
    group_type = None
    spatial_relations = []
    
    if "sitting" in q_lower:
        spatial_relations.append("sitting")
    if "standing" in q_lower:
        spatial_relations.append("standing")
    if "together" in q_lower:
        spatial_relations.append("together")
    if "inside" in q_lower or "in a room" in q_lower:
        spatial_relations.append("inside")

    if any(k in q_lower for k in ["crowd", "large crowd", "huge crowd"]):
        people_present = True
        people_count_bucket = "crowd"
        group_type = "crowd"
    elif any(k in q_lower for k in ["many people", "large group", "lots of people", "group photo", "many people together", "group of people", "people standing"]):
        people_present = True
        people_count_bucket = "large_group"
        group_type = "group_of_people"
    elif any(k in q_lower for k in ["several people", "medium group", "5 people", "6 people"]):
        people_present = True
        people_count_bucket = "medium_group"
        group_type = "group_of_people"
    elif any(k in q_lower for k in ["few people", "a few people", "small group", "3 people", "4 people", "some people"]):
        people_present = True
        people_count_bucket = "small_group"
        group_type = "group_of_people"
    elif any(k in q_lower for k in ["two people", "couple", "two friends", "pair", "2 people", "two person"]):
        people_present = True
        people_count_bucket = "two"
        group_type = "couple"
    elif any(k in q_lower for k in ["one person", "single person", "alone", "1 person", "man", "woman", "portrait"]):
        people_present = True
        people_count_bucket = "one"
        group_type = "individual"
    elif any(k in q_lower for k in ["people together", "people standing", "people sitting", "people gathering"]):
        people_present = True
        group_type = "group_of_people"

    group_modifiers = {
        "one", "two", "three", "four", "five", "six", "many", "few", "several", "large", "small",
        "group", "people", "crowd", "standing", "sitting", "together", "bunch", "persons", "person",
        "gathering", "couple", "pair", "alone", "individual", "lots"
    }

    cleaned_people = [p for p in found_people if p.lower() not in group_modifiers]

    return ParsedClues(
        raw_query=raw_query,
        semantic_query=raw_query.strip(),
        approximate_date=approx_date,
        date_range=date_range,
        people=list(set(cleaned_people)),
        people_present=people_present,
        people_count_bucket=people_count_bucket,
        group_type=group_type,
        spatial_relations=spatial_relations,
        location=list(set(found_locations)),
        event=list(set(found_events)),
        objects=list(set(found_objects)),
        animals=list(set(found_animals)),
        clothing=list(set(found_clothing)),
        colors=list(set(found_colors)),
        activities=list(set(found_activities)),
        environment=env,
        visual_concepts=visual_concepts,
        ocr_text=found_ocr,
        confidence=ConfidenceScores(
            date="medium" if approx_date else "low",
            location="high" if found_locations else "low",
            people="high" if found_people or people_present else "low",
            event="high" if found_events else "low",
            objects="high" if found_objects else "low"
        ),
        is_fallback=True
    )

def parse_query(raw_query: str) -> ParsedClues:
    if not raw_query or not raw_query.strip():
        return ParsedClues(raw_query="", semantic_query="", is_fallback=True)
        
    # Attempt LLM parsing first
    try:
        llm_dict = extract_clues_llm(raw_query)
    except Exception as err:
        logger.warning(f"LLM extraction error: {err}. Defaulting to deterministic fallback parser.")
        llm_dict = None
    
    if llm_dict and isinstance(llm_dict, dict):
        try:
            date_range_data = llm_dict.get("date_range")
            dr_obj = None
            if isinstance(date_range_data, dict) and (date_range_data.get("start") or date_range_data.get("end")):
                dr_obj = DateRange(
                    start=date_range_data.get("start"),
                    end=date_range_data.get("end")
                )
                
            conf_data = llm_dict.get("confidence", {})
            conf_obj = ConfidenceScores(
                date=conf_data.get("date", "medium"),
                location=conf_data.get("location", "medium"),
                people=conf_data.get("people", "medium"),
                event=conf_data.get("event", "medium"),
                objects=conf_data.get("objects", "medium")
            )
            
            raw_llm_ocr = [str(x).lower() for x in (llm_dict.get("ocr_text", []) or [])]
            ocr_list = extract_clean_ocr_text(raw_query, raw_llm_ocr)

            objs_list = llm_dict.get("objects", []) or []
            animals_list = llm_dict.get("animals", []) or []
            clothing_list = llm_dict.get("clothing", []) or []
            colors_list = llm_dict.get("colors", []) or []
            activities_list = llm_dict.get("activities", []) or []
            env_val = llm_dict.get("environment")
            v_concepts_list = llm_dict.get("visual_concepts", []) or []
            
            # Combine deterministic extractions for completeness
            q_lower = raw_query.lower()
            for anim in ANIMAL_KEYWORDS:
                if anim in q_lower and anim not in animals_list:
                    animals_list.append(anim)
            for cloth in CLOTHING_KEYWORDS:
                if cloth in q_lower and cloth not in clothing_list:
                    clothing_list.append(cloth)
            for obj in OBJECT_KEYWORDS:
                if obj in q_lower and obj not in objs_list:
                    objs_list.append(obj)
            for col in COLOR_KEYWORDS:
                if re.search(r'\b' + re.escape(col) + r'\b', q_lower) and col not in colors_list:
                    colors_list.append(col)
            for act in ACTIVITY_KEYWORDS:
                if act in q_lower and act not in activities_list:
                    activities_list.append(act)

            if not env_val:
                if any(k in q_lower for k in ["indoor", "room", "office", "cafeteria", "living room", "home", "house", "table"]):
                    env_val = "indoor"
                elif any(k in q_lower for k in ["outdoor", "beach", "mountain", "park", "jungle", "garden", "green area", "lawn", "river"]):
                    env_val = "outdoor"

            # Strict People group intent & spatial relation extraction
            people_present = None
            people_count_bucket = None
            group_type = None
            spatial_relations = []
            
            if "sitting" in q_lower:
                spatial_relations.append("sitting")
            if "standing" in q_lower:
                spatial_relations.append("standing")
            if "together" in q_lower:
                spatial_relations.append("together")
            if "inside" in q_lower or "in a room" in q_lower:
                spatial_relations.append("inside")

            if any(k in q_lower for k in ["crowd", "large crowd", "huge crowd"]):
                people_present = True
                people_count_bucket = "crowd"
                group_type = "crowd"
            elif any(k in q_lower for k in ["many people", "large group", "lots of people", "group photo", "many people together", "group of people", "people standing"]):
                people_present = True
                people_count_bucket = "large_group"
                group_type = "group_of_people"
            elif any(k in q_lower for k in ["several people", "medium group", "5 people", "6 people"]):
                people_present = True
                people_count_bucket = "medium_group"
                group_type = "group_of_people"
            elif any(k in q_lower for k in ["few people", "a few people", "small group", "3 people", "4 people", "some people"]):
                people_present = True
                people_count_bucket = "small_group"
                group_type = "group_of_people"
            elif any(k in q_lower for k in ["two people", "couple", "two friends", "pair", "2 people", "two person"]):
                people_present = True
                people_count_bucket = "two"
                group_type = "couple"
            elif any(k in q_lower for k in ["one person", "single person", "alone", "1 person", "man", "woman", "portrait"]):
                people_present = True
                people_count_bucket = "one"
                group_type = "individual"
            elif any(k in q_lower for k in ["people together", "people standing", "people sitting", "people gathering"]):
                people_present = True
                group_type = "group_of_people"

            group_modifiers = {
                "one", "two", "three", "four", "five", "six", "many", "few", "several", "large", "small",
                "group", "people", "crowd", "standing", "sitting", "together", "bunch", "persons", "person",
                "gathering", "couple", "pair", "alone", "individual", "lots"
            }
            people_list = llm_dict.get("people", []) or []
            cleaned_people = []
            for p in people_list:
                p_l = str(p).lower().strip()
                if p_l not in group_modifiers and not any(g_phrase in p_l for g_phrase in ["group of people", "many people", "people together", "large group", "group photo"]):
                    cleaned_people.append(p)

            semantic_q = llm_dict.get("semantic_query") or raw_query.strip()

            return ParsedClues(
                raw_query=raw_query,
                semantic_query=semantic_q,
                approximate_date=str(llm_dict.get("approximate_date")) if llm_dict.get("approximate_date") else None,
                date_range=dr_obj,
                people=cleaned_people,
                people_present=people_present,
                people_count_bucket=people_count_bucket,
                group_type=group_type,
                spatial_relations=spatial_relations,
                location=llm_dict.get("location", []) or [],
                event=llm_dict.get("event", []) or [],
                objects=objs_list,
                animals=animals_list,
                clothing=clothing_list,
                colors=colors_list,
                activities=activities_list,
                environment=env_val,
                visual_concepts=v_concepts_list,
                ocr_text=ocr_list,
                confidence=conf_obj,
                is_fallback=False
            )
        except Exception as e:
            logger.warning(f"Error structuring LLM output: {e}. Using fallback parser.")
            
    # Fallback parsing
    return fallback_parse_query(raw_query)
