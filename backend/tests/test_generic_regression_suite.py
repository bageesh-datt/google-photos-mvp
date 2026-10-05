import pytest
from unittest.mock import patch
from backend.app.mvp.schemas import PhotoRecord, VisualSemantics, PeopleSemantics, PhotoLocation, ParsedClues
from backend.app.mvp.query_parser import parse_query, fallback_parse_query
from backend.app.mvp.ranking import rank_photos, calculate_ocr_score, calculate_people_semantic_score
from backend.app.mvp.retrieval import execute_retrieval
from backend.app.mvp.photo_store import get_photo_store

def test_sequential_search():
    """Test A & J: 10 different searches executed sequentially in single session."""
    queries = [
        "charity",
        "lion",
        "SMG",
        "group of people together",
        "beach",
        "2022",
        "Goa beach 2022",
        "birthday with Rohan",
        "many people together",
        "flower spring tour"
    ]
    with patch("backend.app.mvp.query_parser.extract_clues_llm", return_value=None):
        for q in queries:
            clues = parse_query(q)
            results, status = execute_retrieval(clues)
            assert results is not None
            assert len(results) > 0
            assert status in ["success", "zero_matches", "partial_matches", "strong_matches", "weak_matches"]

def test_search_recovery_groq_429():
    """Test B: Groq 429 rate limit fallback."""
    with patch("backend.app.mvp.query_parser.extract_clues_llm", return_value=None):
        clues = parse_query("charity")
        results, status = execute_retrieval(clues)
        assert clues.is_fallback is True
        assert len(results) > 0

def test_search_timeout_groq():
    """Test C: Groq timeout fallback."""
    with patch("backend.app.mvp.query_parser.extract_clues_llm", side_effect=Exception("Groq Timeout")):
        clues = parse_query("group of people together")
        results, status = execute_retrieval(clues)
        assert clues.is_fallback is True
        assert len(results) > 0

def test_charity_semantic_generic():
    """Test D: Generic Photo A (OCR=CHARITY, concept=charity) > Photo B (large group, no charity)."""
    photo_a = PhotoRecord(
        photo_id="GEN_CHARITY",
        filename="charity_drive.jpg",
        image_url="/photos/charity_drive.jpg",
        date="2021-12-25",
        year=2021,
        location=PhotoLocation(city="Bangalore", country="India"),
        event="Charity Drive",
        album="Events",
        description="Community charity drive",
        people=[],
        objects=["charity"],
        visual_concepts=["charity", "donation"],
        ocr_text="CHARITY DRIVE 2021",
        visual_semantics=VisualSemantics(
            objects=["charity"],
            visual_concepts=["charity"],
            ocr_text="CHARITY DRIVE 2021"
        )
    )

    photo_b = PhotoRecord(
        photo_id="GEN_GROUP_NO_CHARITY",
        filename="crowd_party.jpg",
        image_url="/photos/crowd_party.jpg",
        date="2021-12-25",
        year=2021,
        location=PhotoLocation(city="Bangalore", country="India"),
        event="Big Party",
        album="Events",
        description="Crowd of people at a party",
        people=["person1", "person2"],
        objects=["decorations"],
        visual_concepts=["party", "gathering"],
        ocr_text="HAPPY NEW YEAR",
        visual_semantics=VisualSemantics(
            objects=["decorations"],
            visual_concepts=["party"],
            people=PeopleSemantics(present=True, count=10, count_bucket="large_group", group_type="group_of_people"),
            ocr_text="HAPPY NEW YEAR"
        )
    )

    clues = fallback_parse_query("charity")
    ranked = rank_photos([photo_a, photo_b], clues)
    assert ranked[0].photo_id == "GEN_CHARITY"
    assert ranked[0].score > ranked[1].score

def test_group_semantic_generic():
    """Test E: Generic Photo A (large_group) > Photo B (zero people) and Photo C (single person)."""
    photo_a = PhotoRecord(
        photo_id="GEN_LARGE_GROUP",
        filename="group_photo.jpg",
        image_url="/photos/group_photo.jpg",
        date="2022-05-10",
        year=2022,
        location=PhotoLocation(city="Goa", country="India"),
        event="Reunion",
        album="Trips",
        description="Group of friends together",
        people=["Aarav", "Rohan", "Meera", "Priya"],
        objects=["people"],
        visual_concepts=["group photo"],
        ocr_text="",
        visual_semantics=VisualSemantics(
            people=PeopleSemantics(present=True, count=8, count_bucket="large_group", group_type="group_of_people")
        )
    )

    photo_b = PhotoRecord(
        photo_id="GEN_ZERO_PEOPLE",
        filename="mountain_view.jpg",
        image_url="/photos/mountain_view.jpg",
        date="2022-05-10",
        year=2022,
        location=PhotoLocation(city="Manali", country="India"),
        event="Mountain Hike",
        album="Nature",
        description="Scenic mountain range",
        people=[],
        objects=["mountain", "trees"],
        visual_concepts=["landscape"],
        ocr_text="",
        visual_semantics=VisualSemantics(
            people=PeopleSemantics(present=False, count=0, count_bucket="none", group_type="none")
        )
    )

    photo_c = PhotoRecord(
        photo_id="GEN_SINGLE_PERSON",
        filename="portrait.jpg",
        image_url="/photos/portrait.jpg",
        date="2022-05-10",
        year=2022,
        location=PhotoLocation(city="Goa", country="India"),
        event="Solo Trip",
        album="Trips",
        description="Solo portrait at beach",
        people=["Aarav"],
        objects=["person"],
        visual_concepts=["portrait"],
        ocr_text="",
        visual_semantics=VisualSemantics(
            people=PeopleSemantics(present=True, count=1, count_bucket="one", group_type="individual")
        )
    )

    clues = fallback_parse_query("group of people together")
    ranked = rank_photos([photo_a, photo_b, photo_c], clues)
    assert ranked[0].photo_id == "GEN_LARGE_GROUP"
    assert ranked[0].score > ranked[1].score

def test_generic_people_count_fixtures():
    """Test Requirement 14: Generic fixture test for many people, two people, one person."""
    photo_a = PhotoRecord(
        photo_id="FIXTURE_A_LARGE",
        filename="large_group.jpg",
        image_url="/photos/large.jpg",
        date="2023-01-01",
        year=2023,
        location=PhotoLocation(city="Delhi", country="India"),
        event="Reunion Party",
        album="Events",
        description="Large group standing together",
        people=["P1", "P2", "P3"],
        objects=["people"],
        visual_concepts=["gathering"],
        ocr_text="",
        visual_semantics=VisualSemantics(
            people=PeopleSemantics(
                present=True,
                count=12,
                count_bucket="large_group",
                group_type="group_of_people",
                people_context="people standing together"
            )
        )
    )

    photo_b = PhotoRecord(
        photo_id="FIXTURE_B_TWO",
        filename="couple.jpg",
        image_url="/photos/couple.jpg",
        date="2023-01-01",
        year=2023,
        location=PhotoLocation(city="Delhi", country="India"),
        event="Dinner",
        album="Events",
        description="Two people eating together",
        people=["P1", "P2"],
        objects=["people"],
        visual_concepts=["couple"],
        ocr_text="",
        visual_semantics=VisualSemantics(
            people=PeopleSemantics(
                present=True,
                count=2,
                count_bucket="two",
                group_type="couple",
                people_context="two people sitting together"
            )
        )
    )

    photo_c = PhotoRecord(
        photo_id="FIXTURE_C_ZERO",
        filename="mountain.jpg",
        image_url="/photos/mountain.jpg",
        date="2023-01-01",
        year=2023,
        location=PhotoLocation(city="Manali", country="India"),
        event="Trek",
        album="Nature",
        description="Scenic mountain peak",
        people=[],
        objects=["mountain"],
        visual_concepts=["landscape"],
        ocr_text="",
        visual_semantics=VisualSemantics(
            people=PeopleSemantics(
                present=False,
                count=0,
                count_bucket="none",
                group_type="none",
                people_context="no people"
            )
        )
    )

    photo_d = PhotoRecord(
        photo_id="FIXTURE_D_ONE",
        filename="solo.jpg",
        image_url="/photos/solo.jpg",
        date="2023-01-01",
        year=2023,
        location=PhotoLocation(city="Delhi", country="India"),
        event="Solo Portrait",
        album="Portraits",
        description="One person standing outdoor",
        people=["P1"],
        objects=["person"],
        visual_concepts=["portrait"],
        ocr_text="",
        visual_semantics=VisualSemantics(
            people=PeopleSemantics(
                present=True,
                count=1,
                count_bucket="one",
                group_type="individual",
                people_context="one person standing"
            )
        )
    )

    # 1. Query: "many people together" -> A > B > C / D
    clues_many = fallback_parse_query("many people together")
    ranked_many = rank_photos([photo_a, photo_b, photo_c, photo_d], clues_many)
    assert ranked_many[0].photo_id == "FIXTURE_A_LARGE"
    assert ranked_many[0].score > ranked_many[1].score
    assert ranked_many[-1].photo_id == "FIXTURE_C_ZERO"

    # 2. Query: "two people" -> B > D > A > C
    clues_two = fallback_parse_query("two people")
    ranked_two = rank_photos([photo_a, photo_b, photo_c, photo_d], clues_two)
    assert ranked_two[0].photo_id == "FIXTURE_B_TWO"
    assert ranked_two[0].score > ranked_two[1].score

    # 3. Query: "one person" -> D > B > A > C
    clues_one = fallback_parse_query("one person")
    ranked_one = rank_photos([photo_a, photo_b, photo_c, photo_d], clues_one)
    assert ranked_one[0].photo_id == "FIXTURE_D_ONE"
    assert ranked_one[0].score > ranked_one[1].score

def test_contradiction_zero_person_people_query():
    """Test F: Contradiction test - zero person photo must not rank high for people query despite matching text."""
    photo_zero = PhotoRecord(
        photo_id="GEN_CONTRADICTION",
        filename="people_article_scan.jpg",
        image_url="/photos/scan.jpg",
        date="2022-01-01",
        year=2022,
        location=PhotoLocation(city="Delhi", country="India"),
        event="Newspaper Scan",
        album="Documents",
        description="Group of people written in article title",
        people=[],
        objects=["document"],
        visual_concepts=["paper"],
        ocr_text="Group of people gathering article",
        visual_semantics=VisualSemantics(
            people=PeopleSemantics(present=False, count=0, count_bucket="none", group_type="none")
        )
    )

    photo_group = PhotoRecord(
        photo_id="GEN_REAL_GROUP",
        filename="family_gathering.jpg",
        image_url="/photos/family.jpg",
        date="2022-01-01",
        year=2022,
        location=PhotoLocation(city="Delhi", country="India"),
        event="Family Dinner",
        album="Family",
        description="Family members standing together",
        people=["Mom", "Dad", "Aarav"],
        objects=["table", "food"],
        visual_concepts=["family gathering"],
        ocr_text="",
        visual_semantics=VisualSemantics(
            people=PeopleSemantics(present=True, count=6, count_bucket="large_group", group_type="group_of_people")
        )
    )

    clues = fallback_parse_query("group of people together")
    ranked = rank_photos([photo_zero, photo_group], clues)
    assert ranked[0].photo_id == "GEN_REAL_GROUP"

def test_ocr_smg_retrieval():
    """Test G: SMG query retrieves actual SMG photo."""
    store = get_photo_store()
    clues = fallback_parse_query("hat with SMG written on it")
    results, _ = execute_retrieval(clues)
    assert results[0].photo_id in ["P001", "P005"]  # Photo containing SMG hat

def test_visual_lion_retrieval():
    """Test H: lion query retrieves actual lion photo."""
    store = get_photo_store()
    clues = fallback_parse_query("lion")
    results, _ = execute_retrieval(clues)
    assert any("lion" in r.filename.lower() or "lion" in (r.description or "").lower() for r in results[:2])

def test_combined_goa_beach_2022():
    """Test I: Goa beach 2022 retrieves relevant photo."""
    store = get_photo_store()
    clues = fallback_parse_query("Goa beach 2022")
    results, _ = execute_retrieval(clues)
    top = results[0]
    assert top.year == 2022
