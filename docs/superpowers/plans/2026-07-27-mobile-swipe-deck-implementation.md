# Mobile Swipe Deck Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the broken phone layout with a purpose-built swipeable mobile presentation while preserving the existing desktop presentation at widths of 900 pixels and above.

**Architecture:** Keep the presentation as one dependency-free `index.html`. Desktop styles remain the default. A mobile-only media query changes each slide to a scrollable, single-column surface between a fixed-height header and bottom navigation bar. JavaScript keeps one active slide, synchronizes all controls, and treats horizontal swipes as navigation only when they clearly dominate vertical movement.

**Tech Stack:** Semantic HTML, CSS media queries, vanilla JavaScript, Python Playwright with Chromium for viewport regression checks.

## Global Constraints

- Desktop and tablet layout at 900 pixels and above must remain visually and behaviorally unchanged.
- Mobile mode activates below 900 pixels.
- No framework or external dependency.
- Keep all 15 slides, their wording, and their order.
- Swipe must not be the only navigation method.
- Slides may scroll vertically; the page itself must not scroll horizontally.
- Respect `env(safe-area-inset-*)` and `prefers-reduced-motion`.

---

### Task 1: Add viewport regression tests

**Files:**
- Create: `tests/mobile_layout_test.py`
- Test: `index.html`

**Interfaces:**
- Consumes: local `index.html` loaded through a `file://` URL.
- Produces: a zero-exit regression check for viewport overflow, control visibility, slide reachability, mobile stacking, and desktop invariants.

- [ ] **Step 1: Write the failing test**

Create a Playwright script that opens `index.html` at 320×568, 360×800, 390×844, 430×932, 768×1024, and 1440×900. At each mobile viewport assert `document.documentElement.scrollWidth <= window.innerWidth`, the controls are visible, the active slide can scroll when necessary, and all 15 slides are reachable through the Next button. At 1440×900 assert the deck retains a 16:9 aspect ratio and the slide uses the desktop three-row grid.

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/mobile_layout_test.py`

Expected: FAIL on the current mobile layout due to horizontal overflow or overlapping first-slide content.

- [ ] **Step 3: Commit the failing regression test**

```bash
git add tests/mobile_layout_test.py
git commit -m "test: capture mobile presentation overflow"
```

### Task 2: Rebuild the mobile layout in CSS

**Files:**
- Modify: `index.html` mobile media queries and first-slide diagram markup.
- Test: `tests/mobile_layout_test.py`

**Interfaces:**
- Consumes: existing `.app`, `.bar`, `.stage`, `.deck`, `.slide`, `.controls`, and slide component classes.
- Produces: mobile-only layout rules and a reusable `.hero-flow` component that stacks on phones and remains horizontal on desktop.

- [ ] **Step 1: Implement mobile viewport sizing**

Set `.app` to `100dvh` in mobile mode, make `.stage` and `.deck` use `min-height:0`, and make `.slide` use `display:block`, `overflow-y:auto`, `overscroll-behavior:contain`, and safe-area-aware padding. Keep desktop declarations untouched outside the media query.

- [ ] **Step 2: Implement natural mobile document flow**

Make `.head`, `.content`, `.foot`, `.two`, `.three`, `.four`, `.flow`, `.timeline`, and `.arch` stack without absolute or compressed grid rows. Add explicit vertical spacing instead of relying on the desktop `1fr` middle row.

- [ ] **Step 3: Make diagrams phone-safe**

Replace the first slide’s anonymous inline flex container with `.hero-flow`, `.hero-node`, and `.hero-arrow`. Stack these vertically below 900 pixels. Stack status and architecture flows and prevent any child from exceeding `max-width:100%`.

- [ ] **Step 4: Make controls touch-safe**

Give Back, Next, and header controls at least 44×44 CSS pixels. Include safe-area bottom padding and keep controls outside the scrolling slide surface.

- [ ] **Step 5: Run regression tests**

Run: `python3 tests/mobile_layout_test.py`

Expected: PASS at all six viewports.

### Task 3: Harden swipe and navigation behavior

**Files:**
- Modify: `index.html` navigation script.
- Test: `tests/mobile_layout_test.py`

**Interfaces:**
- Consumes: `show(index)`, active slide state, Next and Back controls.
- Produces: boundary-safe swipe navigation and scroll reset for newly activated slides.

- [ ] **Step 1: Add a gesture guard**

Ignore multi-touch input and gestures beginning on buttons, links, inputs, or other interactive elements. Navigate only when horizontal distance is at least 55 pixels and at least 1.35 times the vertical distance.

- [ ] **Step 2: Stop wrapping at swipe boundaries**

A left swipe on the last slide must remain on the last slide, and a right swipe on the first slide must remain on the first slide. The explicit Next button may retain the existing “Start” behavior on the final slide.

- [ ] **Step 3: Reset slide scroll position**

When activating a different slide, set its `scrollTop` to zero so every slide begins at its heading.

- [ ] **Step 4: Run regression tests**

Run: `python3 tests/mobile_layout_test.py`

Expected: PASS with all 15 slides reachable and no overflow.

### Task 4: Validate and publish

**Files:**
- Modify: `index.html`
- Create: `tests/mobile_layout_test.py`
- Existing: `docs/superpowers/specs/2026-07-27-mobile-swipe-deck-design.md`
- Create: `docs/superpowers/plans/2026-07-27-mobile-swipe-deck-implementation.md`

**Interfaces:**
- Produces: tested repository content on `main`.

- [ ] **Step 1: Run full verification**

Run: `python3 tests/mobile_layout_test.py`

Expected: six viewport groups pass, 15 slides reachable, no page-level horizontal overflow, desktop 16:9 layout retained.

- [ ] **Step 2: Inspect screenshots**

Save and inspect screenshots at 390×844 for slide 1 and slide 8, and at 1440×900 for slide 1. Confirm no overlap, clipping, or unintended desktop changes.

- [ ] **Step 3: Publish files**

Update `index.html`, add the test and plan, and use commit message `Fix mobile swipe presentation layout`.

- [ ] **Step 4: Read back and verify repository content**

Fetch the committed `index.html` and confirm the mobile media query, `.hero-flow`, gesture guard, and 15 slide elements are present.
