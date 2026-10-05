# Architecture — Google Photos AI-Assisted Retrieval MVP

## 1. Purpose

This architecture defines the implementation structure for the **Google Photos-style AI-assisted retrieval MVP**.

The MVP focuses on one specific problem:

> Help users retrieve a vaguely remembered photo by turning their natural-language memory into useful retrieval clues, ranking candidate photos, and guiding the user when the first search attempt is weak.

This is a focused prototype, not a full replacement or clone of Google Photos.

---

## 2. Product Goal

### Business goal

Improve the percentage of users who successfully retrieve a photo they remember but cannot precisely describe.

### MVP goal

Reduce the effort between:

**What the user remembers → How the system searches → Finding the intended photo**

### Core experience

```text
User Memory
    ↓
AI Memory Understanding
    ↓
Structured Retrieval Clues
    ↓
Photo Retrieval
    ↓
Candidate Ranking
    ↓
Results + Match Explanation
    ↓
Guided Refinement
    ↓
Photo Found
```

---

## 3. High-Level Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    CONSUMER-FACING MVP                      │
│                                                             │
│  Photos   Search   Albums   Favorites                       │
│                  ↓                                          │
│        Natural Language Memory Input                        │
│                  ↓                                          │
│        Interpreted Clues / Editable Chips                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ HTTP / JSON
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                       FASTAPI BACKEND                       │
│                                                             │
│  /api/mvp/search                                            │
│  /api/mvp/refine                                            │
│  /api/mvp/photos                                            │
│  /api/mvp/photos/{photo_id}                                 │
│                                                             │
│       ↓                                                     │
│  Query Understanding Service                                │
│       ↓                                                     │
│  Retrieval Service                                          │
│       ↓                                                     │
│  Ranking Service                                             │
│       ↓                                                     │
│  Recovery / Refinement Service                              │
└───────────────┬──────────────────────────────┬──────────────┘
                │                              │
                ↓                              ↓
┌─────────────────────────┐        ┌──────────────────────────┐
│    EXISTING GROQ LLM    │        │      PHOTO DATASET       │
│                         │        │                          │
│ Natural language →      │        │ Exactly 50 real demo     │
│ structured clues       │        │ images + metadata         │
└─────────────────────────┘        └──────────────────────────┘

                Existing Discovery Engine
                remains isolated and intact
```

---

## 4. System Boundaries

The project contains two logically separate systems.

### A. Discovery Engine

Purpose:

- analyze user feedback
- create structured observations
- identify recurring retrieval problems
- create evidence-backed opportunity areas

The existing Discovery Engine should remain unchanged unless a clearly required shared utility is reused.

### B. Consumer MVP

Purpose:

- solve the identified retrieval problem in a working prototype
- allow a user to search using vague memory
- retrieve actual photos from the 50-photo demo library
- guide the user through refinement
- measure retrieval-task behaviour

The consumer MVP should have its own routes, services, state and data structures where practical.

---

## 5. Frontend Architecture

### Recommended structure

```text
frontend/
├── src/
│   ├── pages/
│   │   ├── PhotosPage
│   │   ├── SearchPage
│   │   ├── AlbumsPage
│   │   └── FavoritesPage
│   │
│   ├── components/
│   │   ├── AppShell
│   │   ├── BottomNavigation
│   │   ├── SearchBar
│   │   ├── MemoryInput
│   │   ├── ClueChips
│   │   ├── ResultsGrid
│   │   ├── PhotoCard
│   │   ├── MatchExplanation
│   │   ├── RefinementPanel
│   │   ├── PhotoDetail
│   │   └── EmptyState
│   │
│   ├── services/
│   │   └── mvpApi
│   │
│   ├── state/
│   │   └── searchState
│   │
│   └── styles/
│       └── responsive styles
```

### Primary page

The **Search page** is the main MVP surface.

The other navigation items can be lightweight supporting screens so the product feels like a realistic photo application.

---

## 6. Responsive / Mobile-First Architecture

The MVP must work correctly on:

- mobile phones
- tablets
- desktop browsers

Responsive behaviour is a product requirement, not a cosmetic enhancement.

### Mobile layout

Use a single-column layout.

```text
┌───────────────────────────┐
│ Search your photos        │
│                           │
│ [ Describe a memory... ]  │
│                           │
│ I understood:             │
│ [2022] [Goa] [Family]     │
│                           │
│  PHOTO  PHOTO             │
│  PHOTO  PHOTO             │
│                           │
│ Didn't find it?           │
│ [Nearby dates]            │
│ [Add person]              │
│                           │
│ Photos Search Albums ♥    │
└───────────────────────────┘
```

### Desktop layout

Use the available horizontal space for:

- wider search area
- multi-column photo grid
- richer result metadata
- side/refinement panel where appropriate

### Responsive rules

- Photo cards should resize without distortion.
- Search input should remain usable on small screens.
- Clue chips should wrap naturally.
- Refinement actions should remain tappable.
- Do not rely on hover-only interactions.
- Touch targets should be large enough for mobile use.
- Navigation should switch to a compact mobile pattern when viewport width is reduced.
- No horizontal scrolling should be required for normal use.
- Long text should wrap instead of overflowing.
- Results should remain readable at small screen widths.
- Photo detail should become a full-width/mobile-friendly view.
- Loading and empty states should work at all breakpoints.

---

## 7. Backend Architecture

### Suggested structure

```text
backend/
└── app/
    ├── routes/
    │   └── mvp_routes.py
    │
    ├── mvp/
    │   ├── schemas.py
    │   ├── query_parser.py
    │   ├── retrieval.py
    │   ├── ranking.py
    │   ├── refinement.py
    │   ├── explanations.py
    │   └── session.py
    │
    └── data/
        ├── photos/
        └── photo_metadata.json
```

The exact location should be adapted to the existing repository after inspection.

---

## 8. Query Understanding

The user should not need to know the exact search syntax.

Example:

> “Mujhe 2022 ke Goa trip ki family beach photo chahiye.”

The query-understanding service converts the memory into structured clues.

### Expected output

```json
{
  "raw_query": "Mujhe 2022 ke Goa trip ki family beach photo chahiye.",
  "approximate_date": "2022",
  "date_range": {
    "start": "2021-01-01",
    "end": "2023-12-31"
  },
  "people": ["family"],
  "location": ["Goa"],
  "event": ["trip"],
  "objects": ["beach"],
  "visual_concepts": ["beach"],
  "ocr_text": [],
  "confidence": {
    "date": "medium",
    "location": "high",
    "people": "high",
    "event": "medium",
    "objects": "high"
  }
}
```

The exact output should be generated dynamically.

### LLM responsibilities

The existing Groq integration is responsible for:

- extracting clues
- handling natural language
- recognizing approximate dates
- identifying people/place/event/object concepts
- recognizing possible OCR/text intent
- assigning confidence where useful

### Fallback

If the LLM API fails:

- do not crash the application
- use a lightweight deterministic fallback parser where practical
- preserve the raw query
- return a usable response
- clearly separate fallback behaviour from normal LLM behaviour

---

## 9. Photo Data Architecture

The MVP must contain **exactly 50 real demo photos**.

### Photo storage

```text
data/
├── photos/
│   ├── P001.jpg
│   ├── P002.jpg
│   ├── ...
│   └── P050.jpg
│
└── photo_metadata.json
```

### Metadata schema

Each photo should include:

```json
{
  "photo_id": "P023",
  "image_path": "photos/P023.jpg",
  "date": "2022-06-18",
  "location": "Goa",
  "people": ["family"],
  "event": "trip",
  "objects": ["beach"],
  "ocr_text": "",
  "album": "Goa Trip 2022"
}
```

Metadata may be expanded with additional fields when useful, but the schema should remain consistent across all 50 photos.

---

## 10. Dataset Design Principles

The dataset should not contain 50 unrelated random pictures.

It should intentionally support vague-memory retrieval scenarios such as:

- family
- friends
- travel
- places
- birthdays
- celebrations
- documents
- visible text
- food
- objects
- activities
- approximate time periods
- albums

The dataset should contain **near-matches**.

Example:

```text
P019 → Goa, 2021, friends, beach
P023 → Goa, 2022, family, beach
P027 → Mumbai, 2022, family, dinner
```

For a memory such as:

> “family beach photo from Goa around 2022”

the correct photo should rank higher because several independent metadata signals match.

This enables a meaningful ranking demo.

---

## 11. Retrieval Architecture

Retrieval should be actual retrieval from the 50-photo dataset.

### Candidate generation

Use the extracted clues to generate candidate photos using available signals such as:

- date
- date range
- location
- people
- event
- object
- OCR text
- album
- textual similarity
- semantic similarity where practical

### Important requirement

No query-specific hardcoded mappings.

Do not implement:

```text
if query == "family beach Goa":
    return P023
```

Instead:

```text
query
  ↓
clues
  ↓
candidate matching
  ↓
score calculation
  ↓
ranking
```

---

## 12. Ranking Architecture

Use a weighted scoring model.

Conceptually:

```text
final_score =
    date_score
  + location_score
  + people_score
  + event_score
  + object_score
  + ocr_score
  + semantic_score
```

Weights should be configurable in one place.

Example starting weights:

```json
{
  "date": 0.20,
  "location": 0.20,
  "people": 0.15,
  "event": 0.15,
  "objects": 0.10,
  "ocr": 0.10,
  "semantic": 0.10
}
```

These are implementation starting points, not validated product targets.

The ranking service should:

1. normalize individual signals
2. calculate a final score
3. keep the score interpretable
4. sort candidates
5. return top results
6. expose matched signals for explanation

---

## 13. Match Explanation

Every result should be explainable using actual matched fields.

Example:

```text
Why this matched
✓ Approximate year matches
✓ Goa matches
✓ Family context matches
✓ Beach concept matches
```

The explanation layer should derive these statements from actual ranking signals.

Do not hardcode explanations for specific photos or queries.

---

## 14. Guided Recovery / Refinement

The recovery loop is a core part of the MVP.

### Weak first attempt

If the result set is empty or weak:

```text
Didn't find the right photo?

Try:
[Broaden the date]
[Add a person]
[Try the location]
[Search visible text]
[Try another clue]
```

### Refinement logic

Suggestions should use:

- extracted clues
- missing clues
- low-scoring signals
- result distribution
- original memory
- previous attempts

### Refinement cycle

```text
Attempt 1
   ↓
Weak Results
   ↓
Suggested Refinement
   ↓
Updated Clues
   ↓
Attempt 2
   ↓
Better Results
   ↓
Photo Found
```

The user should be able to perform multiple refinements without restarting.

---

## 15. Search Session State

Maintain lightweight session state:

```json
{
  "session_id": "...",
  "initial_query": "...",
  "current_clues": {},
  "attempt_number": 2,
  "refinements": [
    "broadened date"
  ],
  "result_count": 8,
  "selected_photo": "P023"
}
```

This enables MVP testing of retrieval effort.

Do not persist sensitive user data beyond what is necessary for the prototype.

---

## 16. API Architecture

### `POST /api/mvp/search`

Input:

```json
{
  "query": "family beach photo from Goa around 2022"
}
```

Response should include:

- parsed clues
- ranked results
- result explanations
- refinement suggestions
- session identifier

### `POST /api/mvp/refine`

Input:

```json
{
  "session_id": "...",
  "refinement": {
    "type": "date_range",
    "value": "broader"
  }
}
```

Response:

- updated clues
- updated ranked results
- updated refinement suggestions
- attempt number

### `GET /api/mvp/photos`

Returns the demo photo library or a filtered subset.

### `GET /api/mvp/photos/{photo_id}`

Returns details for one photo.

---

## 17. Frontend-to-Backend Flow

```text
User enters memory
        ↓
POST /api/mvp/search
        ↓
Query Parser
        ↓
Structured clues
        ↓
Retrieval Engine
        ↓
Ranking Engine
        ↓
Explanation Engine
        ↓
Refinement Engine
        ↓
JSON response
        ↓
Frontend renders:
clues + photo grid + explanations + recovery actions
```

---

## 18. Error Handling

### LLM failure

Show:

> “We couldn't fully interpret the memory. You can still try searching with the original description.”

Use fallback parsing where possible.

### No results

Show recovery suggestions instead of a dead end.

### Weak results

Show:

> “We found a few possible matches.”

Then provide refinements.

### Invalid photo

Skip the broken item and log the issue rather than breaking the entire grid.

### Backend/API failure

Show an understandable UI state:

> “Something went wrong. Please try again.”

Do not expose stack traces to the user.

---

## 19. Security and Configuration

Use existing project configuration for:

- Groq API key
- LLM model
- server configuration
- environment-specific settings

Never commit API keys.

Use `.env` locally and `.env.example` for configuration documentation.

Do not send unnecessary personal information to the LLM.

---

## 20. Testing Architecture

### Backend tests

Cover:

- query parsing
- approximate-date handling
- people extraction
- location extraction
- event/object extraction
- candidate generation
- ranking
- partial-clue retrieval
- zero-result handling
- weak-result handling
- refinement generation
- refinement execution
- successful retrieval

### Frontend tests

Cover:

- search input
- loading state
- clues rendering
- result grid
- empty state
- refinement actions
- photo selection
- responsive rendering

### Regression testing

Existing Discovery Engine tests must continue to pass.

The MVP should not introduce regressions into the existing pipeline.

---

## 21. Observability for MVP Testing

Track task-level events needed for product evaluation:

```text
search_started
memory_submitted
clues_generated
results_shown
refinement_used
results_refreshed
photo_selected
search_abandoned
```

For the prototype, lightweight in-memory or local logging is sufficient.

Do not collect unnecessary personal data.

---

## 22. MVP Success Metrics

### North Star

**Vague-Memory Photo Retrieval Success Rate**

Definition:

> Percentage of eligible vague-memory retrieval tasks where the user finds and confirms the intended photo.

### Supporting metrics

- time to first useful result
- recovery success rate
- number of refinements
- manual browsing effort
- search abandonment
- result relevance
- user-reported confusion/friction

For the initial MVP, establish a baseline through testing before setting numeric targets.

---

## 23. User Testing Architecture

### Required research validation

Before finalizing the product direction:

**5–6 user interviews**

Focus:

- what users remember
- first retrieval attempt
- recovery behaviour
- failure point
- what users expect from search

### MVP usability test

Test the prototype with at least:

**3 target users**

Observe:

1. Can they describe the memory naturally?
2. Do they understand the extracted clues?
3. Are results relevant?
4. Can they use the refinement loop?
5. Can they complete the retrieval task?
6. Where do they hesitate or abandon?

Do not invent testing results before the sessions are actually run.

---

## 24. Deployment Considerations

The MVP should run locally first and be deployable later.

### Local

```text
Frontend
   ↕
FastAPI
   ↕
Groq + 50-photo dataset
```

### Deployment

Use environment variables for LLM configuration.

The demo dataset can be bundled with the prototype when deployment constraints allow it.

If serverless deployment is used, avoid depending on:

- persistent local writes
- background jobs that must survive the request
- process memory as a durable database

The current MVP does not require persistent user accounts or long-term user data storage.

---

## 25. Non-Goals

The first MVP does not attempt to build:

- a full Google Photos replacement
- real user account authentication
- cloud photo backup
- full-scale photo synchronization
- production-grade computer vision infrastructure
- every existing Google Photos feature
- a production-scale search index

The MVP only needs to prove the focused product concept:

> **Can AI help a user turn a vague memory into a successful photo retrieval path?**

---

## 26. Key Architecture Principles

### Evidence-driven

The MVP direction comes from the Discovery Engine and subsequent user research.

### Generic

Retrieval logic must work on arbitrary supported memories.

### Explainable

Users should understand why results appeared.

### Recoverable

A failed first attempt should lead to a useful next step.

### Real

The MVP must retrieve actual photos from the 50-photo dataset.

### Responsive

The full experience must work on mobile and desktop.

### Modular

The MVP should remain logically separate from the Discovery Engine.

### Testable

Every major stage should be independently testable.

---

## 27. Final MVP Architecture

```text
                         USER
                          │
                          ▼
                ┌───────────────────┐
                │ Google Photos-    │
                │ style UI          │
                │ Responsive        │
                │ Mobile + Desktop  │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ Memory Search     │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ Groq Query        │
                │ Understanding     │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ Structured Clues  │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ Candidate         │
                │ Retrieval         │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ Ranking           │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ Results +         │
                │ Match Explanation │
                └─────────┬─────────┘
                          │
                ┌─────────┴─────────┐
                │                   │
           Strong result        Weak result
                │                   │
                ▼                   ▼
        ┌──────────────┐    ┌────────────────┐
        │ Photo Found  │    │ Guided         │
        │              │    │ Refinement     │
        └──────────────┘    └───────┬────────┘
                                    │
                                    └──────► Retrieval
```

This architecture is the implementation blueprint for the MVP and should be used together with `problemStatement.md`.
