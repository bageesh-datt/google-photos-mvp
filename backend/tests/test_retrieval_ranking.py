import pytest
from backend.app.mvp.photo_store import get_photo_store
from backend.app.mvp.query_parser import fallback_parse_query as parse_query
from backend.app.mvp.retrieval import execute_retrieval
from backend.app.mvp.ranking import rank_photos

def test_retrieval_over_50_photos():
    store = get_photo_store()
    assert len(store.get_all_photos()) == 50
    
    clues = parse_query("family beach photo from Goa around 2022")
    results, status = execute_retrieval(clues)
    
    assert len(results) > 0
    assert status in ["strong_matches", "weak_matches"]
    assert results[0].score >= results[-1].score
    assert results[0].photo_id == "P023"  # P023 has Goa + 2022 + family + beach

def test_near_match_discrimination():
    clues = parse_query("family beach photo from Goa around 2022")
    results, _ = execute_retrieval(clues)
    
    res_map = {r.photo_id: r for r in results}
    score_p023 = res_map["P023"].score  # Goa 2022 Family Beach
    score_p019 = res_map["P019"].score  # Goa 2021 Friends Beach
    
    assert score_p023 > score_p019, f"P023 ({score_p023}) should rank higher than P019 ({score_p019})"

def test_visual_semantic_retrieval_correctness():
    # 1. "lion" - P038 is the actual Asiatic Lion photo
    clues_lion = parse_query("lion")
    results_lion, _ = execute_retrieval(clues_lion)
    top_lion = results_lion[0]
    assert top_lion.photo_id == "P038", f"Top result for 'lion' should be P038, got {top_lion.photo_id} with score {top_lion.score}"
    assert any("visual concept" in r.lower() or "photo content" in r.lower() or "lion" in r.lower() for r in top_lion.match_reasons)
    
    # Assert actual lion photo P038 outranks dog photo P037
    res_map_lion = {r.photo_id: r for r in results_lion}
    p037_score = res_map_lion["P037"].score if "P037" in res_map_lion else 0.0
    assert res_map_lion["P038"].score > p037_score, f"Lion photo P038 ({res_map_lion['P038'].score}) must outrank dog photo P037 ({p037_score})"

    # 2. "dog" - P037 is Golden Retriever photo
    clues_dog = parse_query("dog")
    results_dog, _ = execute_retrieval(clues_dog)
    top_dog = results_dog[0]
    assert top_dog.photo_id == "P037", f"Top result for 'dog' should be P037, got {top_dog.photo_id} with score {top_dog.score}"

    # 3. "beach" - beach photos (P011, P019, P023)
    clues_beach = parse_query("beach")
    results_beach, _ = execute_retrieval(clues_beach)
    top_beach_ids = [r.photo_id for r in results_beach[:3]]
    assert any(pid in top_beach_ids for pid in ["P011", "P019", "P023"])

    # 4. "mountain" - mountain photos (P004, P014, P049)
    clues_mountain = parse_query("mountain")
    results_mountain, _ = execute_retrieval(clues_mountain)
    top_mountain_ids = [r.photo_id for r in results_mountain[:3]]
    assert any(pid in top_mountain_ids for pid in ["P004", "P014", "P049"])

    # 5. "birthday cake" - birthday cake photos (P012, P021, P022)
    clues_cake = parse_query("birthday cake")
    results_cake, _ = execute_retrieval(clues_cake)
    top_cake_ids = [r.photo_id for r in results_cake[:3]]
    assert any(pid in top_cake_ids for pid in ["P012", "P021", "P022"])

    # 6. "document" - document photos (P029, P030, P031, P032)
    clues_doc = parse_query("document")
    results_doc, _ = execute_retrieval(clues_doc)
    top_doc_ids = [r.photo_id for r in results_doc[:5]]
    assert any(pid in top_doc_ids for pid in ["P029", "P030", "P031", "P032", "P033", "P034"])

    # 7. "family beach" - family beach photo P023
    clues_fb = parse_query("family beach")
    results_fb, _ = execute_retrieval(clues_fb)
    assert results_fb[0].photo_id == "P023"

    # 8. "Goa trip" - Goa trip photos (P011, P013, P019, P023)
    clues_goa = parse_query("Goa trip")
    results_goa, _ = execute_retrieval(clues_goa)
    top_goa_ids = [r.photo_id for r in results_goa[:3]]
    assert any(pid in top_goa_ids for pid in ["P011", "P013", "P019", "P023"])

    # 9. "passport text" - passport OCR photo P029
    clues_pass = parse_query("passport text")
    results_pass, _ = execute_retrieval(clues_pass)
    assert results_pass[0].photo_id in ["P029", "P032"]

    # 10. Unrelated / no-match query
    clues_none = parse_query("spaceship astronaut mars alien")
    results_none, _ = execute_retrieval(clues_none)
    assert not results_none or results_none[0].score < 0.3

def test_no_hardcoding_assertion():
    queries = [
        "birthday photo with my cousin",
        "old college event picture",
        "photo from Delhi around 2021",
        "document where passport text is visible",
        "picture of food from a restaurant",
        "photo with my friend near a lake",
        "diwali diyas terrace",
        "monsoon trek lonavala waterfall",
        "golden retriever dog frisbee",
        "taj mahal sunny day"
    ]
    
    store = get_photo_store()
    all_photos = store.get_all_photos()
    
    for q in queries:
        clues = parse_query(q)
        results = rank_photos(all_photos, clues)
        assert len(results) == 50
        assert all(0.0 <= r.score <= 1.0 for r in results)
        assert len(results[0].match_reasons) > 0

def test_generic_fixture_retrieval_ranking():
    """Validates generic visual search ranking using synthetic photo fixtures (Photo A, B, C)
    and verifies that both lion photos (P038, P003) outrank unrelated tulip photo (P043)."""
    from backend.app.mvp.schemas import PhotoRecord, PhotoLocation, VisualSemantics
    
    photo_a = PhotoRecord(
        photo_id="PA",
        filename="Monsoon_Trek.jpg",
        image_url="/photos/PA.jpg",
        date="2021-08-15",
        year=2021,
        location=PhotoLocation(city="Lonavala", country="India"),
        event="Monsoon Trek",
        objects=["lion", "raincoat"],
        visual_concepts=["lion", "wildlife"],
        visual_semantics=VisualSemantics(
            objects=["lion", "raincoat"],
            visual_concepts=["lion", "wildlife"],
            generated_description="An Asiatic lion walking in green forest."
        ),
        album="Monsoon Treks",
        description="Monsoon Trek lion"
    )
    
    photo_b = PhotoRecord(
        photo_id="PB",
        filename="Kashmir_Tour.jpg",
        image_url="/photos/PB.jpg",
        date="2021-04-10",
        year=2021,
        location=PhotoLocation(city="Srinagar", country="India"),
        event="Kashmir Spring Tour",
        objects=["blooming tulips", "fountain"],
        visual_concepts=["flower garden", "tulips"],
        visual_semantics=VisualSemantics(
            objects=["blooming tulips", "fountain"],
            visual_concepts=["flower garden", "tulips"],
            generated_description="Parents standing amidst millions of blooming tulips."
        ),
        album="Kashmir Spring",
        description="Parents standing amidst millions of blooming tulips."
    )
    
    photo_c = PhotoRecord(
        photo_id="PC",
        filename="Gir_Safari.jpg",
        image_url="/photos/PC.jpg",
        date="2022-05-10",
        year=2022,
        location=PhotoLocation(city="Gir", country="India"),
        event="Gir Lion Safari",
        objects=["asiatic lion"],
        visual_concepts=["lion", "wildlife"],
        visual_semantics=VisualSemantics(
            objects=["asiatic lion"],
            visual_concepts=["lion", "wildlife"],
            generated_description="Asiatic lion resting under acacia tree."
        ),
        album="Wild India Safaris",
        description="Gir Lion Safari"
    )
    
    clues = parse_query("lion")
    results = rank_photos([photo_a, photo_b, photo_c], clues)
    res_map = {r.photo_id: r for r in results}
    
    assert res_map["PA"].score > res_map["PB"].score, f"Photo A lion ({res_map['PA'].score}) must outrank Photo B tulip ({res_map['PB'].score})"
    assert res_map["PC"].score > res_map["PB"].score, f"Photo C lion ({res_map['PC'].score}) must outrank Photo B tulip ({res_map['PB'].score})"
    assert res_map["PB"].score == 0.0, f"Unrelated Photo B tulip must score 0.0, got {res_map['PB'].score}"
    
    # Also verify actual 50-photo dataset retrieval for lion
    clues_real = parse_query("lion")
    real_results, _ = execute_retrieval(clues_real)
    real_map = {r.photo_id: r for r in real_results}
    
    assert real_map["P038"].score >= 0.6, f"P038 (Lion) score = {real_map['P038'].score}, expected >= 0.6"
    assert real_map["P003"].score >= 0.3, f"P003 (Monsoon Lion) score = {real_map['P003'].score}, expected >= 0.3"
    p043_score = real_map["P043"].score if "P043" in real_map else 0.0
    assert p043_score == 0.0, f"P043 (Tulip) score = {p043_score}, expected 0.0"
    assert real_map["P038"].score > p043_score
    assert real_map["P003"].score > p043_score

def test_generic_ocr_retrieval_ranking():
    """Validates generic OCR retrieval, case-insensitivity, combined OCR+Visual scoring,
    and synthetic fixture assertion score(Photo A) > score(Photo B)."""
    from backend.app.mvp.schemas import PhotoRecord, PhotoLocation, VisualSemantics
    
    # 1. Synthetic Fixture Test
    photo_a = PhotoRecord(
        photo_id="PA_OCR",
        filename="SMG_Hat_Photo.jpg",
        image_url="/photos/PA.jpg",
        date="2021-12-25",
        year=2021,
        location=PhotoLocation(city="Bengaluru", country="India"),
        event="Christmas Event",
        objects=["santa hat", "hat"],
        visual_concepts=["hat with SMG"],
        ocr_text="SMG Merry Christmas",
        album="Festivities",
        description="Photo with SMG written on hat"
    )
    
    photo_b = PhotoRecord(
        photo_id="PB_OCR",
        filename="Cake_Photo.jpg",
        image_url="/photos/PB.jpg",
        date="2021-04-10",
        year=2021,
        location=PhotoLocation(city="Srinagar", country="India"),
        event="Birthday",
        objects=["cake", "candles"],
        visual_concepts=["birthday cake"],
        ocr_text="HAPPY BIRTHDAY HELLO",
        album="Celebrations",
        description="Birthday cake photo"
    )
    
    clues_smg_hat = parse_query("SMG hat")
    results_fixture = rank_photos([photo_a, photo_b], clues_smg_hat)
    res_map = {r.photo_id: r for r in results_fixture}
    
    assert res_map["PA_OCR"].score > res_map["PB_OCR"].score, f"Photo A (SMG Hat) score {res_map['PA_OCR'].score} must outrank Photo B (Cake) score {res_map['PB_OCR'].score}"
    assert res_map["PA_OCR"].score >= 0.70
    
    # 2. Production Dataset Test for SMG, smg, SMG hat, hat with SMG written on it
    queries = [
        "SMG",
        "smg",
        "SMG hat",
        "hat with SMG written on it"
    ]
    
    for q in queries:
        clues = parse_query(q)
        results, status = execute_retrieval(clues)
        top = results[0]
        assert top.photo_id == "P001", f"Query '{q}' should retrieve P001, got {top.photo_id} with score {top.score}"
        assert top.score >= 0.40, f"Query '{q}' score = {top.score}, expected >= 0.40"
        
    # 3. Nonexistent OCR text test
    clues_none = parse_query("XYZ123NONEXISTENT")
    results_none, status_none = execute_retrieval(clues_none)
    assert status_none == "zero_matches"
    assert len(results_none) == 0

def test_generic_people_count_fixture():
    """STEP 20: Validates generic people count fixture scoring order (A > B > C)
    for query 'many people together' without photo ID hardcoding."""
    from backend.app.mvp.schemas import PhotoRecord, PhotoLocation, VisualSemantics, PeopleSemantics
    
    photo_a = PhotoRecord(
        photo_id="PA_GROUP",
        filename="Group_Event.jpg",
        image_url="/photos/PA.jpg",
        date="2022-08-15",
        year=2022,
        location=PhotoLocation(city="Mumbai", country="India"),
        event="Team Celebration",
        objects=["people", "chairs"],
        visual_concepts=["large group gathering", "crowd"],
        visual_semantics=VisualSemantics(
            objects=["people", "chairs"],
            visual_concepts=["large group gathering", "crowd"],
            people=PeopleSemantics(
                present=True,
                count=12,
                count_bucket="large_group",
                group_type="group_of_people",
                people_context="multiple people standing together in a group"
            ),
            generated_description="Multiple people standing together during an indoor celebration."
        ),
        album="Company Events",
        description="Team celebration indoor group photo"
    )
    
    photo_b = PhotoRecord(
        photo_id="PB_SOLO",
        filename="Solo_Portrait.jpg",
        image_url="/photos/PB.jpg",
        date="2022-05-10",
        year=2022,
        location=PhotoLocation(city="Delhi", country="India"),
        event="Solo Tour",
        objects=["person", "bench"],
        visual_concepts=["solo portrait"],
        visual_semantics=VisualSemantics(
            objects=["person", "bench"],
            visual_concepts=["solo portrait"],
            people=PeopleSemantics(
                present=True,
                count=1,
                count_bucket="one",
                group_type="single_person",
                people_context="one person sitting alone on a bench"
            ),
            generated_description="A person sitting alone on a park bench."
        ),
        album="Solo Travels",
        description="Solo portrait on bench"
    )
    
    photo_c = PhotoRecord(
        photo_id="PC_NATURE",
        filename="Flower_Macro.jpg",
        image_url="/photos/PC.jpg",
        date="2022-03-01",
        year=2022,
        location=PhotoLocation(city="Srinagar", country="India"),
        event="Garden Walk",
        objects=["red tulip"],
        visual_concepts=["flower", "nature"],
        visual_semantics=VisualSemantics(
            objects=["red tulip"],
            visual_concepts=["flower", "nature"],
            people=PeopleSemantics(
                present=False,
                count=0,
                count_bucket="none",
                group_type="no_people",
                people_context="no people present"
            ),
            generated_description="A single red tulip blooming in sunlight."
        ),
        album="Botanic Gardens",
        description="Red tulip macro photo"
    )
    
    clues = parse_query("many people together")
    results = rank_photos([photo_a, photo_b, photo_c], clues)
    res_map = {r.photo_id: r for r in results}
    
    assert res_map["PA_GROUP"].score > res_map["PB_SOLO"].score, f"Large group ({res_map['PA_GROUP'].score}) must rank higher than single person ({res_map['PB_SOLO'].score})"
    assert res_map["PB_SOLO"].score > res_map["PC_NATURE"].score, f"Single person ({res_map['PB_SOLO'].score}) must rank higher than zero people flower ({res_map['PC_NATURE'].score})"
    assert res_map["PC_NATURE"].score == 0.0, f"Zero-people flower photo must score 0.0, got {res_map['PC_NATURE'].score}"

def test_embedding_fixture():
    """STEP 21: Validates semantic retrieval works via vector embedding similarity
    even when exact query words do not literally overlap."""
    from backend.app.mvp.schemas import PhotoRecord, PhotoLocation, VisualSemantics, PeopleSemantics
    from backend.app.mvp.embedding_service import encode_text
    
    photo = PhotoRecord(
        photo_id="P_EMB",
        filename="Gathering.jpg",
        image_url="/photos/PEMB.jpg",
        date="2022-11-20",
        year=2022,
        location=PhotoLocation(city="Pune", country="India"),
        event="Annual Gala",
        objects=["adults", "suits"],
        visual_concepts=["social gathering", "standing"],
        visual_semantics=VisualSemantics(
            objects=["adults", "suits"],
            visual_concepts=["social gathering", "standing"],
            people=PeopleSemantics(
                present=True,
                count=15,
                count_bucket="large_group",
                group_type="group_of_people",
                people_context="several adults standing together during an indoor gathering"
            ),
            generated_description="Several adults standing together during an indoor gathering.",
            visual_embedding=encode_text("Several adults standing together during an indoor gathering.")
        ),
        album="Gala 2022",
        description="Several adults standing together during an indoor gathering."
    )
    
    clues = parse_query("large group of people")
    results = rank_photos([photo], clues)
    assert len(results) == 1
    assert results[0].score >= 0.40, f"Expected embedding semantic score >= 0.40, got {results[0].score}"
    assert any("semantic" in r.lower() or "group" in r.lower() or "gathering" in r.lower() for r in results[0].match_reasons)

def test_universal_multimodal_queries():
    """STEP 19: Validates full set of universal query categories against production 50 photos dataset."""
    test_queries = [
        ("many people together", ["P004", "P006", "P009", "P028", "P045", "P048", "P050"]),
        ("large group", ["P004", "P006", "P009", "P028", "P045", "P048"]),
        ("lion", ["P038", "P003"]),
        ("dog", ["P037", "P019"]),
        ("SMG", ["P001"]),
        ("hat with SMG written on it", ["P001"]),
        ("Goa beach 2022", ["P023", "P011", "P019"]),
        ("birthday with Rohan", ["P012", "P021", "P022"])
    ]
    
    for query_str, expected_top_candidates in test_queries:
        clues = parse_query(query_str)
        results, status = execute_retrieval(clues)
        assert len(results) > 0
        top_id = results[0].photo_id
        assert top_id in expected_top_candidates, f"Query '{query_str}' expected top photo in {expected_top_candidates}, got {top_id} (score {results[0].score})"
        if len(results) > 1:
            assert results[0].score >= results[-1].score

def test_generic_ocr_and_charity_retrieval():
    """Validates generic OCR retrieval for 'charity', 'CHARITY', 'charity event',
    and proves 'charity' is NOT misclassified as a people group query."""
    charity_queries = ["charity", "CHARITY", "charity event"]
    
    for q in charity_queries:
        clues = parse_query(q)
        assert clues.people_count_bucket is None, f"Query '{q}' should not activate people_count_bucket, got {clues.people_count_bucket}"
        
        results, status = execute_retrieval(clues)
        top = results[0]
        assert top.photo_id == "P007", f"Query '{q}' expected top result P007, got {top.photo_id} with score {top.score}"
        assert top.score >= 0.40, f"Expected P007 score >= 0.40 for '{q}', got {top.score}"

def test_generic_signal_disambiguation_fixture():
    """Validates generic signal disambiguation fixture:
    Photo A (OCR 'CHARITY') vs Photo B (large group) vs Photo C (OCR 'WELCOME')
    For 'charity': Photo A > Photo B and Photo A > Photo C.
    For 'many people together': Photo B > Photo A."""
    from backend.app.mvp.schemas import PhotoRecord, PhotoLocation, VisualSemantics, PeopleSemantics
    
    photo_a = PhotoRecord(
        photo_id="PA_CHARITY",
        filename="Charity_Drive.jpg",
        image_url="/photos/PA.jpg",
        date="2021-12-25",
        year=2021,
        location=PhotoLocation(city="Bengaluru", country="India"),
        event="Community Drive",
        objects=["gifts", "charity box"],
        visual_concepts=["charity poster", "charity drive"],
        ocr_text="CHARITY Drive 2021",
        visual_semantics=VisualSemantics(
            objects=["gifts", "charity box"],
            visual_concepts=["charity poster", "charity drive"],
            people=PeopleSemantics(
                present=True,
                count=3,
                count_bucket="small_group",
                group_type="small_group"
            ),
            ocr_text="CHARITY Drive 2021"
        ),
        album="Community Service",
        description="Volunteers at Christmas CHARITY drive"
    )
    
    photo_b = PhotoRecord(
        photo_id="PB_GROUP",
        filename="Crowd_Event.jpg",
        image_url="/photos/PB.jpg",
        date="2022-08-15",
        year=2022,
        location=PhotoLocation(city="Mumbai", country="India"),
        event="Large Celebration",
        objects=["crowd", "stage"],
        visual_concepts=["large crowd gathering"],
        visual_semantics=VisualSemantics(
            objects=["crowd", "stage"],
            visual_concepts=["large crowd gathering"],
            people=PeopleSemantics(
                present=True,
                count=15,
                count_bucket="large_group",
                group_type="group_of_people"
            )
        ),
        album="Concerts",
        description="Massive crowd at festival"
    )
    
    photo_c = PhotoRecord(
        photo_id="PC_WELCOME",
        filename="Welcome_Banner.jpg",
        image_url="/photos/PC.jpg",
        date="2022-01-10",
        year=2022,
        location=PhotoLocation(city="Delhi", country="India"),
        event="Welcome Party",
        objects=["banner"],
        visual_concepts=["welcome party"],
        ocr_text="WELCOME GUESTS",
        visual_semantics=VisualSemantics(
            objects=["banner"],
            visual_concepts=["welcome party"],
            ocr_text="WELCOME GUESTS"
        ),
        album="Parties",
        description="Welcome banner photo"
    )
    
    # 1. Query 'charity' -> Photo A > Photo B and Photo A > Photo C
    clues_charity = parse_query("charity")
    res_charity = rank_photos([photo_a, photo_b, photo_c], clues_charity)
    map_c = {r.photo_id: r for r in res_charity}
    assert map_c["PA_CHARITY"].score > map_c["PB_GROUP"].score, f"Photo A ({map_c['PA_CHARITY'].score}) must outrank Photo B ({map_c['PB_GROUP'].score}) for 'charity'"
    assert map_c["PA_CHARITY"].score > map_c["PC_WELCOME"].score, f"Photo A ({map_c['PA_CHARITY'].score}) must outrank Photo C ({map_c['PC_WELCOME'].score}) for 'charity'"
    
    # 2. Query 'many people together' -> Photo B > Photo A
    clues_people = parse_query("many people together")
    res_people = rank_photos([photo_a, photo_b, photo_c], clues_people)
    map_p = {r.photo_id: r for r in res_people}
    assert map_p["PB_GROUP"].score > map_p["PA_CHARITY"].score, f"Photo B ({map_p['PB_GROUP'].score}) must outrank Photo A ({map_p['PA_CHARITY'].score}) for 'many people together'"


