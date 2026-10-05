import os
import sys
from dotenv import load_dotenv

# Load env variables BEFORE importing settings
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from backend.app.config import Settings
# Re-instantiate settings with loaded env
settings = Settings()

from backend.app.mvp.query_parser import parse_query
from backend.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def run_live_verification():
    groq_configured = bool(settings.GROQ_API_KEY and len(settings.GROQ_API_KEY) > 5)
    
    live_groq_pass = False
    first_q_pass = False
    second_q_pass = False
    errors = []
    
    # 1. Test live Groq request
    if groq_configured:
        try:
            clues = parse_query("family beach photo from Goa around 2022")
            if not clues.is_fallback and clues.confidence:
                live_groq_pass = True
            else:
                errors.append("Groq request fell back to deterministic parser")
        except Exception as e:
            errors.append(f"Groq API error: {e}")
    else:
        errors.append("GROQ_API_KEY is not configured")
        
    # 2. Test First Query End-to-End Flow
    try:
        q1 = "family beach photo from Goa around 2022"
        res1 = client.post("/api/mvp/search", json={"query": q1})
        if res1.status_code == 200:
            d1 = res1.json()
            sid1 = d1["session_id"]
            results1 = d1["results"]
            refinements1 = d1["refinements"]
            
            # Refine
            ref_res1 = client.post("/api/mvp/refine", json={
                "session_id": sid1,
                "action_id": refinements1[0]["id"] if refinements1 else "ref_broaden_date",
                "updated_clues": {"people": ["family"], "location": ["Goa"]}
            })
            
            # Confirm
            top_photo_id = results1[0]["photo_id"] if results1 else "P023"
            conf_res1 = client.post("/api/mvp/confirm", json={
                "session_id": sid1,
                "selected_photo_id": top_photo_id
            })
            
            if ref_res1.status_code == 200 and conf_res1.status_code == 200:
                first_q_pass = True
            else:
                errors.append("First query refinement or confirm failed")
        else:
            errors.append(f"Search endpoint returned {res1.status_code}")
    except Exception as e:
        errors.append(f"First query E2E exception: {e}")
        
    # 3. Test Second Arbitrary Query End-to-End Flow
    try:
        q2 = "document where passport text is visible"
        res2 = client.post("/api/mvp/search", json={"query": q2})
        if res2.status_code == 200:
            d2 = res2.json()
            sid2 = d2["session_id"]
            results2 = d2["results"]
            
            top_photo_id2 = results2[0]["photo_id"] if results2 else "P029"
            conf_res2 = client.post("/api/mvp/confirm", json={
                "session_id": sid2,
                "selected_photo_id": top_photo_id2
            })
            
            if conf_res2.status_code == 200 and len(results2) == 50:
                second_q_pass = True
            else:
                errors.append("Second query confirm or candidate count failed")
        else:
            errors.append(f"Second query search endpoint returned {res2.status_code}")
    except Exception as e:
        errors.append(f"Second query E2E exception: {e}")
        
    # Print ONLY required format (NO API key values exposed)
    print("--- FINAL LIVE MVP VERIFICATION REPORT ---")
    print(f"GROQ configured: {'YES' if groq_configured else 'NO'}")
    print(f"live Groq request: {'PASS' if live_groq_pass else 'FAIL'}")
    print(f"first query end-to-end: {'PASS' if first_q_pass else 'FAIL'}")
    print(f"second arbitrary query end-to-end: {'PASS' if second_q_pass else 'FAIL'}")
    if errors:
        print(f"errors: {'; '.join(errors)}")
    else:
        print("errors: None")

if __name__ == "__main__":
    run_live_verification()
