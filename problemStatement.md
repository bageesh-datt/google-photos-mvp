# Google Photos — AI-Powered Vague-Memory Retrieval MVP

## 1. Project Context

This MVP is part of the Google Photos Core Experience project.

The business goal is to increase the percentage of users who successfully retrieve a photo they remember but cannot precisely describe when they start searching.

The project should move beyond the generic problem of *“users find it difficult to search for old photos”* and focus on the reason retrieval fails even when the user still remembers useful context about the photo.

The Discovery Engine is used to surface retrieval-related signals from user feedback. The MVP then turns the validated problem into a focused consumer-facing experience.

---

## 2. Business Problem

### Business Metric

**Successful retrieval of vaguely remembered photos**

The product should help more users complete a photo-retrieval task when they remember the photo through incomplete or approximate clues rather than exact searchable details.

### Product Outcome

Help the user move from:

**Memory → Retrieval path → Useful results → Successful retrieval**

The goal is not to make users better at guessing search terms. The goal is to help the product understand the memory they already have and guide them toward the photo.

---

## 3. User Problem

When trying to retrieve an older photo, a user may remember things such as:

- an approximate year, month, or time period
- a person or group of people
- a place
- an event or occasion
- an object or activity
- the visual context of the photo
- text visible inside the photo

But the user may not remember the exact date, filename, album, searchable wording, or other precise metadata.

When the first search path does not work, the user may:

- try different keywords
- change or broaden the date
- search using another clue
- browse the timeline manually
- check albums
- repeat the process through different paths
- abandon the retrieval attempt

### Core user pain

> **The user remembers the photo through context, but does not always know how to translate that memory into a retrieval path that will surface the right photo.**

---

## 4. Target User

### Frequent Vague-Memory Photo Retriever

An active Google Photos user who regularly tries to retrieve older photos from incomplete or approximate memories.

Typical characteristics of the segment:

- remembers the context of a photo
- lacks exact searchable details
- tries more than one retrieval path when the first attempt fails
- values finding a specific meaningful photo rather than simply browsing the library

The segment is defined by **retrieval behaviour**, not demographics.

---

## 5. Core Retrieval Scenario

A representative user might say:

> “Mujhe 2022 ke around Goa trip ki family beach photo chahiye.”

The user knows the photo exists and remembers several clues, but may not know:

- the exact date
- the exact place metadata
- the exact search wording
- the album in which it was stored
- which single clue will retrieve it

The MVP should allow the user to start with this kind of natural-language memory.

---

## 6. Root Cause Hypothesis

### Memory-to-Retrieval Translation Gap

Users naturally remember photos as a combination of context and clues.

Photo retrieval systems require those memories to be translated into searchable signals and retrieval paths.

When that translation is weak, the user has to discover the correct retrieval strategy through trial and error.

### Working hypothesis

> **Users can often remember enough about a meaningful photo to recognize it, but turning that memory into a reliable retrieval path requires too much guessing, refinement, or manual browsing.**

This remains a working hypothesis until it is validated and refined through the required user interviews.

---

## 7. Problem Definition

> **Frequent Google Photos users can remember the context of an older photo but may not remember the exact searchable details. When their memory does not map cleanly to a reliable retrieval path, they must repeatedly guess, broaden or change queries, adjust dates, or manually browse, making successful retrieval unnecessarily effortful.**

---

## 8. Product Opportunity

Instead of asking the user to discover the perfect query, the product can help translate their memory into useful retrieval clues and guide them when the first attempt is weak.

### Opportunity statement

> **Help users turn vague, contextual memories into actionable retrieval clues and guide them through recovery until they can identify the intended photo.**

---

# 9. MVP Definition

## MVP Name / Concept

### AI-Assisted Memory Search

A Google Photos-style photo retrieval experience focused specifically on vague-memory retrieval.

The MVP is **not a full Google Photos clone**. It is a focused working prototype that demonstrates the identified retrieval solution.

---

## 10. MVP User Journey

The complete experience should work as:

**1. Open Photos**  
↓  
**2. Go to Search**  
↓  
**3. Describe the photo from memory**  
↓  
**4. AI interprets the memory into clues**  
↓  
**5. User reviews/edits the clues**  
↓  
**6. System retrieves and ranks candidate photos**  
↓  
**7. User evaluates the results**  
↓  
**8. System offers guided refinement when results are weak**  
↓  
**9. User finds and confirms the intended photo**

---

## 11. MVP Functional Scope

### A. Memory-Based Search Input

The main search experience should accept natural-language descriptions such as:

> “family beach photo from Goa around 2022”

The user should not need to know a special search syntax.

### B. AI Clue Extraction

The system should interpret the memory into structured clues such as:

- approximate date/date range
- people
- location
- event
- objects/activity
- visual concepts
- OCR/text clues

The clues should be visible to the user.

Example:

`2022`  `Goa`  `Family`  `Beach`  `Trip`

The user should be able to remove or edit a clue before or during retrieval.

### C. Real Photo Retrieval

The MVP should search a controlled demo library of **exactly 50 real photos**.

Each photo should have structured metadata such as:

- photo ID
- image
- date
- location
- people
- event
- objects
- OCR/text
- album

The retrieval system should rank candidates using available matching signals rather than returning hardcoded results.

### D. Candidate Results

Results should be shown in a photo grid similar to a modern photo application.

Each candidate can display:

- thumbnail/image
- date
- relevant metadata
- match score or relative match strength
- why the result matched

### E. Why This Matched

The interface should explain relevant matching signals based on the actual candidate metadata.

Example:

- Approximate year matches
- Goa matches
- Family context matches
- Beach concept matches

Explanations must be generated from actual matched fields, not query-specific hardcoding.

### F. Guided Recovery / Refinement

If the first attempt does not surface a useful result, the experience should not end with a dead-end “No results” message.

Instead, the system should guide the user toward another retrieval path.

Possible refinement actions include:

- try nearby dates
- add a person
- try the place
- search visible text
- broaden the concept
- browse related photos

The refinement options should depend on the current query, extracted clues, and result quality.

### G. Successful Retrieval State

When the user identifies the intended photo, show a clear completion state such as:

**Photo found**

Then show the selected photo and relevant metadata.

The experience should make successful task completion obvious.

---

# 12. Demo Dataset Requirement

The MVP will use **exactly 50 real photos** for the controlled demo library.

The 50 photos should intentionally cover multiple vague-retrieval scenarios, including:

- family and friends
- trips and places
- birthdays and events
- documents and text-visible photos
- food, objects, and activities
- approximate-date retrieval
- album-related scenarios

The dataset should contain similar and near-match photos so that the ranking and refinement experience can be demonstrated meaningfully.

### Important implementation rule

There must be **no hardcoded query → photo mappings**.

For example, the product must not contain logic such as:

```text
if query == "family beach photo":
    return P023
```

The system must retrieve candidates from the 50-photo library using actual metadata/search signals.

---

# 13. Google Photos-Style Experience

The UI should feel like a modern photo library while remaining an original project interface rather than an exact copy of Google Photos branding.

Suggested high-level navigation:

**Photos | Search | Albums | Favorites**

The primary focus of the MVP is the **Search** experience.

### Key visual expectations

- clean photo-grid layout
- image-first interface
- simple search interaction
- clear metadata hierarchy
- lightweight cards/chips for interpreted clues
- clear retrieval/refinement actions
- obvious success state

---

# 14. Responsive Requirement

The MVP must be **fully responsive**.

It should work as a real product experience across:

### Desktop

- multi-column photo grid
- full navigation
- comfortable search width
- visible metadata and refinement controls

### Tablet

- adaptive photo grid
- compact navigation
- flexible search/results layout

### Mobile

The experience should genuinely feel like a mobile photo application, not a desktop page squeezed into a smaller screen.

Mobile requirements:

- single-column or compact photo grid depending on screen width
- touch-friendly buttons and clue chips
- responsive search bar
- readable result cards
- mobile-friendly navigation
- no horizontal scrolling
- no clipped or overlapping text
- images must resize without distortion
- refinement actions must remain easy to tap
- sufficient spacing around interactive elements

### Responsive rule

Use responsive layout techniques such as:

- CSS Grid/Flexbox
- fluid widths
- responsive breakpoints
- relative sizing where appropriate
- mobile-first behaviour for critical interactions

The MVP should be tested at common desktop and mobile viewport sizes before final delivery.

---

# 15. MVP Non-Goals

The first MVP does not need to reproduce the complete functionality of Google Photos.

Out of scope for this version:

- full personal Google Photos account integration
- complete cloud photo synchronization
- production-scale storage
- full Google Photos feature parity
- complete native mobile app deployment
- population-level measurement claims

The MVP exists to demonstrate and test the **vague-memory photo retrieval experience**.

---

# 16. Validation Plan

The product direction should be validated in two stages.

### Stage 1 — User Interviews

Conduct the required **5–6 user interviews** to validate:

- what users naturally remember
- what clues they try first
- how they recover after failed retrieval
- where they struggle most
- whether the memory-to-retrieval translation gap accurately describes the problem

### Stage 2 — MVP User Testing

Test the MVP with **at least 3 target users**.

Observe:

- whether the user can describe the photo naturally
- whether the interpreted clues make sense
- whether useful candidates are surfaced
- whether the user understands the refinement suggestions
- how many attempts/path changes are required
- whether the user successfully retrieves the intended photo
- where the experience creates confusion or friction

Do not fabricate user-testing results before the testing is completed.

---

# 17. Success Measurement

### North Star

**Vague-Memory Photo Retrieval Success Rate**

Definition:

> Share of eligible vague-memory retrieval tasks where the user finds and confirms the intended photo.

### Supporting measures

- time to first useful result
- recovery success rate after a weak first attempt
- number of search/refinement attempts
- manual browsing effort
- result relevance
- retrieval abandonment
- user-reported friction/confusion

For the MVP, establish a baseline through user testing before setting numeric targets.

---

# 18. Key Product Principles

### 1. Start from memory, not search syntax

The user should be able to describe what they remember naturally.

### 2. Treat memory as a combination of clues

A meaningful retrieval attempt may contain multiple partial signals rather than one perfect keyword.

### 3. Retrieval should be recoverable

A weak first attempt should lead to a useful next step rather than a dead end.

### 4. Keep the user in control

Users should be able to see, remove, edit, and refine interpreted clues.

### 5. Evidence before assumptions

The product direction should be refined using Discovery Engine evidence, user interviews, and MVP user testing.

---

# 19. Traceability to Discovery Work

The Discovery Engine provides the evidence layer behind the product direction:

**Raw user feedback**
→ **Structured observations**
→ **Recurring retrieval problems**
→ **Opportunity areas**
→ **User research validation**
→ **Problem definition**
→ **MVP**

The MVP should address the specific problem identified through this process rather than becoming a generic AI photo-search demo.

---

# 20. Working Conclusion

The working product problem is:

> **Users often remember an older photo through context, but that memory does not always translate into a clear retrieval path. The MVP should bridge that gap by interpreting the user's memory as clues, retrieving relevant candidates, and guiding the user when the first path fails.**

The MVP is successful only when it demonstrates a complete, usable retrieval journey:

**Describe memory → Understand clues → Retrieve → Refine → Find the photo**

