# Implementation Architecture & Technical Specification — Google Photos AI-Assisted Retrieval MVP

## 1. Overview & Architectural Mapping

This document provides the complete, authoritative implementation mapping for the **Google Photos-Style AI-Assisted Vague-Memory Retrieval MVP**, connecting the product requirements in [`problemStatement.md`](file:///c:/Users/mishr/OneDrive/Desktop/AI%20Projects/google-photos-mvp/problemStatement.md) and system designs in [`architecture.md`](file:///c:/Users/mishr/OneDrive/Desktop/AI%20Projects/google-photos-mvp/architecture.md) to the actual codebase, backend services, frontend components, and dataset schemas of this repository.

The primary objective of this MVP is to solve the **Memory-to-Retrieval Translation Gap** by translating natural language vague memories into structured retrieval clues, executing signal-based multi-attribute photo search over a controlled 50-photo dataset, offering transparent match explanations, and guiding users through an interactive recovery loop when search results are weak.

---

## 2. Repository Structure & Boundary Verification

### A. Completed Workspace Files (`c:\Users\mishr\OneDrive\Desktop\AI Projects\google-photos-mvp`)

```text
google-photos-mvp/
├── architecture.md                     # High-level architecture specification
├── problemStatement.md                 # Product & user problem statement
├── implementation.md                 # Complete technical & file mapping document
├── requirements.txt                   # Backend Python dependencies (FastAPI, uvicorn, groq, pillow, pytest)
├── .env.example                       # Environment configuration template
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entrypoint with CORS & static mounting
│   │   ├── config.py                  # Pydantic settings & configurable weights loader
│   │   │
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── mvp_routes.py          # REST endpoints (/api/mvp/search, /refine, /photos, /confirm)
│   │   │
│   │   ├── mvp/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py             # Pydantic data schemas (ParsedClues, PhotoRecord, RankedResult, etc.)
│   │   │   ├── groq_client.py         # Groq LLM integration (llama-3.3-70b-versatile JSON output)
│   │   │   ├── query_parser.py        # LLM memory parser + regex/taxonomy fallback parser
│   │   │   ├── photo_store.py         # In-memory photo metadata indexer
│   │   │   ├── retrieval.py           # Multi-signal candidate retrieval engine
│   │   │   ├── ranking.py             # Multi-attribute scoring engine with zero query hardcoding
│   │   │   ├── explanations.py        # Dynamic match reason generator
│   │   │   ├── refinement.py          # Guided recovery action generator
│   │   │   └── session.py             # Search session state manager
│   │   │
│   │   └── data/
│   │       ├── photo_metadata.json    # Standardized metadata for all 50 demo photos
│   │       └── photos/                # 50 real demo JPEG images (P001.jpg .. P050.jpg)
│   │
│   └── tests/
│       ├── test_dataset_validation.py # Automated validation verifying exactly 50 photos & metadata mapping
│       ├── test_query_parser.py       # Query understanding & fallback parser unit tests
│       ├── test_retrieval_ranking.py  # Multi-signal scoring & zero-hardcoding verification tests
│       ├── test_refinement.py         # Guided recovery options & clue updating tests
│       └── test_api_routes.py         # End-to-end FastAPI endpoint integration tests
│
└── frontend/
    ├── package.json                   # Node dependencies (React, Vite, Lucide icons)
    ├── vite.config.js                 # Vite dev server & API proxy config
    ├── index.html                     # HTML root entrypoint with Google Fonts (Inter, Outfit)
    │
    └── src/
        ├── main.jsx                   # React DOM mount point
        ├── App.jsx                    # Root App component
        ├── index.css                  # Modern Google Photos design system (CSS tokens, grid, animations)
        │
        ├── pages/
        │   ├── SearchPage.jsx         # Primary MVP workspace & recovery interface
        │   ├── PhotosPage.jsx         # Library view of all 50 demo photos
        │   ├── AlbumsPage.jsx         # Collection cards view
        │   └── FavoritesPage.jsx      # Favorited gallery view
        │
        ├── components/
        │   ├── AppShell.jsx           # Frame layout with tab navigation
        │   ├── Header.jsx             # Top bar with Google Photos logo & tabs
        │   ├── BottomNavigation.jsx   # Mobile bottom navigation bar
        │   ├── SearchBar.jsx          # Conversational search input bar
        │   ├── MemoryInput.jsx        # Sample memory prompt chips
        │   ├── ClueChips.jsx          # Editable / removable structured clue pill chips
        │   ├── ResultsGrid.jsx        # Photo candidates grid
        │   ├── PhotoCard.jsx          # Photo card with score badge & "Why matched" trigger
        │   ├── MatchExplanation.jsx   # Dynamic match reason breakdown
        │   ├── RefinementPanel.jsx    # Guided recovery options bar
        │   ├── PhotoDetailModal.jsx   # Full-screen photo viewer + metadata sidebar + confirm button
        │   ├── SuccessBanner.jsx      # "Photo Found" completion state banner
        │   └── EmptyState.jsx         # Recoverable zero/weak result state
        │
        └── services/
            └── mvpApi.js              # Fetch client communicating with FastAPI backend
```

### B. Discovery Engine Isolation

The Discovery Engine remains in `../google-photos-discovery-engine` completely isolated:
- Zero runtime dependencies between projects.
- Regression check confirmed **43 passed in 6.53s** on `google-photos-discovery-engine`.

---

## 3. 50-Photo Dataset & Metadata Schema

- **Count**: Exactly 50 real demo images (`P001.jpg` .. `P050.jpg`) located in both `backend/app/data/photos/` and `frontend/public/photos/`.
- **Validation**: Enforced via `test_dataset_count_and_integrity()`.
- **Categories Covered**: Family/Friends, Trips/Places, Birthdays/Events, Documents/OCR, Food/Activities, Approximate-date/Seasonal, and College/Reunion Albums.
- **Near-Matches**: `P023` (Goa 2022 Family Beach) vs `P019` (Goa 2021 Friends Beach) vs `P012` (Delhi Birthday).

---

## 4. Query Parsing & Groq Integration

- **LLM Model**: `llama-3.3-70b-versatile` in JSON mode.
- **Structured Clues**: `approximate_date`, `date_range`, `people`, `location`, `event`, `objects`, `visual_concepts`, `ocr_text`, `confidence`.
- **Fallback**: Regex & taxonomy-based parser in `query_parser.py` handles unconfigured API key or network failures safely without crashing.

---

## 5. Multi-Signal Retrieval & Generic Weighted Ranking

- **Formula**:
  $$S_i = \sum_{k} w_k \cdot s_{k,i}$$
  with $w_{\text{date}}=0.20, w_{\text{loc}}=0.20, w_{\text{people}}=0.15, w_{\text{event}}=0.15, w_{\text{objects}}=0.10, w_{\text{ocr}}=0.10, w_{\text{semantic}}=0.10$.
- **Strict Rule**: Zero hardcoded query-to-photo maps exist. Verified dynamically across 10 arbitrary test queries in `test_no_hardcoding_assertion()`.

---

## 6. Guided Recovery & Search Session State

- **Weak/Zero Result Recovery**: `refinement.py` generates dynamic recovery actions (broaden date range, add people context, search OCR text, remove restrictive place filter).
- **Multi-Turn Session**: `SessionManager` tracks attempt count, clue revisions, result quality, and task confirmation.

---

## 7. Responsive UI & Test Results

- **Breakpoints**: Mobile (<640px), Tablet (640-1024px), Desktop (>1024px) supported with sticky bottom navigation, minimum 44px touch targets, and zero horizontal scroll.
- **Test Pass**:
  - Discovery Engine Baseline / Regression: **43 passed in 6.53s**
  - MVP Backend Test Suite: **42 passed in 32.68s**
  - Frontend Production Build: **1489 modules built in 2.84s** with 0 errors.

---

## 8. Vercel Deployment & Production Specification

### A. Vercel Serverless Architecture
The MVP is configured for seamless single-origin deployment on Vercel:
- **Serverless Entrypoint**: `api/index.py` exposes the FastAPI ASGI `app` object to Vercel Python runtime.
- **Frontend SPA & Static Assets**: Built via Vite (`frontend/dist`) and served from Vercel Edge CDN.
- **Static Photos**: 50 physical JPEG images (`frontend/public/photos/P001.jpg` .. `P050.jpg`) served directly at `/photos/*.jpg` via Edge CDN.

### B. Production Dependency Optimization & Bundle Size
- **Excluded Heavy Packages**: PyTorch (`torch`), `sentence-transformers`, and HuggingFace weights are excluded from `requirements.txt` to keep the serverless function bundle size under 15 MB (well below Vercel's 250 MB limit).
- **Runtime Vector Matching**: Uses pre-computed 384-dimensional dense vectors stored in `backend/app/data/photo_metadata.json` + NumPy cosine similarity + lightweight query encoding fallback in `embedding_service.py`.

### C. Vercel Project Configuration (`vercel.json`)
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "includeFiles": "backend/app/data/photo_metadata.json"
      }
    },
    {
      "src": "frontend/package.json",
      "use": "@vercel/vite"
    }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "api/index.py" },
    { "src": "/photos/(.*)", "dest": "/photos/$1" },
    { "src": "/(.*)", "dest": "frontend/$1" }
  ]
}
```

### D. Production Environment Variables
Set in Vercel Dashboard (**Project Settings $\rightarrow$ Environment Variables**):
- `GROQ_API_KEY`: Groq Cloud API Key for JSON memory parsing (`llama-3.3-70b-versatile`).
- *(Optional)* `GROQ_MODEL`: `openai/gpt-oss-120b` or `llama-3.3-70b-versatile`.

