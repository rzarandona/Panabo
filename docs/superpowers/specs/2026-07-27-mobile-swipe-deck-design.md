# Mobile Swipe Deck Design

## Goal

Create a phone-first presentation experience for the Panabo Digital Permit Pilot while preserving the current desktop presentation unchanged.

## Scope

The implementation will remain inside the existing `index.html` file. Desktop behavior and layout will remain intact. Mobile behavior will activate only on viewports below 900 pixels.

## Mobile Experience

- Display one slide at a time in a full-screen mobile deck.
- Support horizontal swipe gestures for previous and next navigation.
- Retain visible Back and Next controls as an accessible fallback.
- Use large touch targets of at least 44 by 44 CSS pixels.
- Respect device safe areas using `env(safe-area-inset-*)`.
- Keep the current slide number and progress indicator visible without covering content.
- Prevent accidental browser-page horizontal scrolling during slide gestures.
- Preserve vertical scrolling inside a slide when its content exceeds the available phone height.
- Keep keyboard navigation working for desktop and external keyboards.

## Responsive Boundary

- Desktop and tablet layout at 900 pixels and above: no visual or behavioral changes.
- Mobile layout below 900 pixels: dedicated swipe-deck presentation.
- Extra compact adjustments below 560 pixels for narrow phones.

## Layout

### Mobile Header

A compact sticky header will contain:

- Panabo project identity
- Current slide title or deck label
- Overview button

### Mobile Slide Surface

Each slide will:

- Occupy the available viewport between the header and navigation bar.
- Use a single-column content flow.
- Increase body-text readability and spacing.
- Convert multi-column cards, flows, and diagrams into stacked or horizontally scrollable structures where necessary.
- Keep diagrams legible without shrinking text below a usable size.

### Mobile Navigation

A sticky bottom control bar will contain:

- Back button
- Slide counter
- Progress indicator
- Next button

The bar will include bottom safe-area padding for devices with home indicators.

## Interaction Model

### Swipe

- A deliberate horizontal swipe changes slides.
- Small or mostly vertical movements do not trigger navigation.
- Swiping right moves to the previous slide.
- Swiping left moves to the next slide.
- Navigation stops at the first and last slides.

### Overview

The existing overview remains available. On mobile it will use a full-screen grid or list with large selectable slide targets.

### Motion

- Use short transform and opacity transitions.
- Respect `prefers-reduced-motion` by disabling or minimizing animation.

## Accessibility

- Buttons will have descriptive `aria-label` values.
- Navigation state will be communicated through the visible counter and progress indicator.
- Focus states will remain visible.
- Swipe will never be the only navigation method.
- Text contrast will preserve the current accessible light and dark slide treatments.
- Content remains usable at browser zoom and larger system text settings.

## Technical Approach

The existing HTML structure and slide content will be retained. The update will consist of:

1. Mobile-specific CSS within the existing media queries.
2. Touch and pointer gesture handling in the existing JavaScript navigation layer.
3. Small semantic and accessibility enhancements to navigation controls.
4. No framework or external dependency.
5. No separate `mobile.html` file.

## Error and Edge Handling

- Ignore multi-touch gestures.
- Cancel navigation when the gesture begins on an interactive control.
- Avoid slide changes during predominantly vertical scrolling.
- Reset temporary drag transforms after cancelled gestures.
- Keep the active slide index synchronized across swipe, buttons, dots, keyboard navigation, and overview selection.
- Recalculate viewport sizing after orientation changes.

## Validation

The implementation should be checked at representative viewport sizes:

- 320 × 568
- 360 × 800
- 390 × 844
- 430 × 932
- 768 × 1024
- 1440 × 900 to confirm desktop remains unchanged

Validation should cover:

- All 15 slides are reachable.
- Swipe directions are correct.
- Vertical slide scrolling does not accidentally navigate.
- Back and Next controls remain reachable.
- Safe-area spacing works on notched devices.
- No content is clipped permanently.
- Desktop layout and controls remain visually unchanged.
- Print behavior remains intact.

## Out of Scope

- PWA installation
- Offline caching
- Native app packaging
- Separate mobile content
- Changes to presentation wording or slide order
- Redesign of the desktop presentation

## Success Criteria

The mobile presentation feels purpose-built for a phone, can be operated comfortably with one hand, preserves all presentation content, and introduces no visible change to the existing desktop experience.
