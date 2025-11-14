# US-001: Onboarding - Sélection Niveau d'Adoption

**Epic**: Onboarding & First-Time User Experience
**Priority**: P0 (Critical - Must Have)
**Story Points**: 5
**Sprint**: 1
**Related Wireframe**: `wireframes/01-onboarding-adoption-level.html`

---

## User Story

**As a** new user arriving on Lexikon for the first time
**I want to** choose my adoption level based on my intended usage pattern
**So that** I receive a tailored onboarding experience matching my needs and timeline

---

## Context & Problem

**UX Analysis Reference**: Friction Point #8 - One-Size-Fits-All Onboarding

Users have vastly different temporal usage patterns:
- **Students**: Need ontology for 6-12 months (thesis period)
- **Researchers**: Periodic use over 1-2 years (research project)
- **Developers**: Continuous long-term integration (production API)

A single generic onboarding fails to address these different contexts, leading to:
- Students overwhelmed by features they'll never use
- Developers frustrated by missing API documentation
- Researchers unsure about validation workflows

**Solution**: Differentiated onboarding based on three adoption levels.

---

## Acceptance Criteria

### Functional Requirements

- [ ] **Display 3 radio card options** (mutually exclusive selection)
  - Quick Project (student/temporary)
  - Research Project (academic/periodic)
  - Production API (developer/continuous)

- [ ] **Each card displays**:
  - Icon (emoji or SVG)
  - Title
  - Subtitle (user type + duration)
  - Quoted user statement (persona quote)
  - 3 key features (bullet list)
  - Pricing badge (Free, Pro €49/mo, Team €199/mo)

- [ ] **Selection behavior**:
  - Only one card selectable at a time (radio button pattern)
  - Visual feedback on hover (border color change, shadow, translateY)
  - Selected state: blue left border (4px) + radio indicator filled

- [ ] **CTA "Continuer →" button**:
  - Disabled by default (opacity 50%, cursor not-allowed)
  - Enabled only when a selection is made
  - Primary style (blue background, white text)
  - Transitions to next onboarding step on click

- [ ] **"Pas sûr ? → Quiz 2 minutes" link**:
  - Ghost button style (transparent background, gray text)
  - Links to interactive quiz (helps users choose level)

### Non-Functional Requirements

- [ ] **Performance**:
  - Page loads in < 1 second
  - Radio selection responds in < 100ms

- [ ] **Accessibility (WCAG AA)**:
  - Radio inputs have proper ARIA labels
  - Keyboard navigation functional (Tab, Space/Enter to select)
  - Focus states visible (2px blue ring)
  - Color contrast ratio > 4.5:1 for all text

- [ ] **Responsive Design**:
  - Desktop (1440px): Cards horizontal or vertical (design choice)
  - Tablet (768px): Cards stack vertically
  - Mobile (375px): Cards stack vertically, font-size reduced

- [ ] **Analytics Tracking**:
  - Track distribution of selections (which level chosen)
  - Track time spent on page
  - Track quiz link click-through rate

---

## Technical Notes

### Components Used

- **RadioCard** (custom component to create)
  - Props: `value`, `name`, `icon`, `title`, `subtitle`, `quote`, `features[]`, `badge`
  - State: `checked`, `hovered`
  - Events: `onChange`

- **Button** (existing: `src/lib/components/Button.svelte`)
  - Variant: `primary`
  - Size: `md`
  - Props: `disabled`, `onClick`

### Data Model

```typescript
interface AdoptionLevel {
  id: 'quick-project' | 'research-project' | 'production-api';
  icon: string;
  title: string;
  subtitle: string;
  quote: string;
  features: string[];
  badge: {
    text: string;
    type: 'free' | 'pro' | 'team';
  };
}
```

### API Endpoints

**POST `/api/onboarding/adoption-level`**

Request:
```json
{
  "user_id": "uuid",
  "adoption_level": "quick-project",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

Response:
```json
{
  "success": true,
  "next_step": "/onboarding/profile",
  "recommended_tier": "free"
}
```

### State Management

Store adoption level in:
1. **LocalStorage** (key: `lexikon-onboarding-level`) - for persistence across page reloads
2. **User Profile** (database) - once user creates account
3. **Analytics** (event: `onboarding_level_selected`)

### Validation Rules

- Required field: Must select one option before proceeding
- No backend validation needed (radio ensures single selection)

---

## Design Tokens Used

```css
/* Colors */
--color-primary-600: #2563eb;   /* Selected state, CTA button */
--color-primary-500: #3b82f6;   /* Hover state, badges */
--color-gray-200: #e5e7eb;      /* Card borders (default) */
--color-gray-700: #374151;      /* Text color */

/* Spacing */
--space-4: 1rem;   /* Card internal padding */
--space-6: 1.5rem; /* Card padding */
--space-8: 2rem;   /* Section margins */

/* Radius */
--radius-xl: 0.75rem; /* Card border radius */

/* Shadow */
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);  /* Card hover */
```

---

## Edge Cases & Error Handling

| Scenario | Behavior |
|----------|----------|
| User refreshes page mid-selection | Restore selection from localStorage if exists |
| User navigates back from step 2 | Pre-select previously chosen level |
| No selection made, tries to continue | Button disabled, show validation message |
| JavaScript disabled | Fallback to standard radio buttons + server-side handling |
| Quiz link broken | Show error toast, allow manual selection |

---

## Test Cases

### Unit Tests

```javascript
// Example test structure
describe('Onboarding Adoption Level', () => {
  it('disables continue button when no selection', () => {
    // Test implementation
  });

  it('enables continue button when level selected', () => {
    // Test implementation
  });

  it('allows only one selection at a time', () => {
    // Test implementation
  });

  it('persists selection to localStorage', () => {
    // Test implementation
  });

  it('applies correct styles to selected card', () => {
    // Test implementation
  });
});
```

### E2E Tests

1. **Happy Path**:
   - Visit onboarding page
   - Click "Quick Project" card
   - Verify CTA button enabled
   - Click "Continuer"
   - Verify navigation to next step

2. **Quiz Flow**:
   - Click "Quiz 2 minutes" link
   - Complete quiz
   - Verify auto-selection based on quiz result

3. **Accessibility**:
   - Navigate using keyboard only
   - Verify ARIA labels read correctly by screen reader

---

## Definition of Done

- [ ] Code implemented and merged to `main`
- [ ] Unit tests passing (> 80% coverage)
- [ ] E2E tests passing (happy path + quiz flow)
- [ ] Accessibility audit passed (WCAG AA)
- [ ] Cross-browser tested (Chrome, Firefox, Safari)
- [ ] Responsive tested (mobile, tablet, desktop)
- [ ] Analytics events firing correctly
- [ ] Design review approved by UX Designer
- [ ] Code review approved by 2 developers
- [ ] Documentation updated (component README)

---

## Dependencies

- **Blocks**: US-002 (Profile Setup) - needs adoption level to determine fields
- **Requires**: Design tokens implemented, Button component ready

---

## Open Questions

- [ ] Should we show pricing upfront or reveal after selection? (Current: upfront)
- [ ] Should quiz be modal or separate page? (Current: separate page recommended)
- [ ] Do we track abandonments at this step? (Recommendation: yes)

---

## References

- **UX Analysis**: `docs/analyses/analyse-ux-parcours-critiques-v03.md` (Section: Dimension Temporelle)
- **Wireframe**: `wireframes/01-onboarding-adoption-level.html`
- **Design System**: `docs/design/design-tokens.css`
- **Component**: To create `src/lib/components/RadioCard.svelte`

---

**Created**: 2025-11-14
**Last Updated**: 2025-11-14
**Status**: Ready for Development
