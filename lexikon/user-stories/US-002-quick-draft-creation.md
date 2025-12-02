# US-002: Quick Draft - Création Rapide de Terme

**Epic**: Term Creation & Management
**Priority**: P0 (Critical - Must Have)
**Story Points**: 8
**Sprint**: 1
**Related Wireframe**: `wireframes/02-creation-quick-draft.html`

---

## User Story

**As a** user who selected "Quick Project" adoption level (or wants fast term creation)
**I want to** create a term with minimal required fields in under 5 minutes
**So that** I can quickly build my ontology without being blocked by complex forms

---

## Context & Problem

**UX Analysis Reference**: Friction Point #1 - 60-Minute Term Creation

Current problem:
- Creating a single term takes **60 minutes** (all fields required)
- Users abandon the form (52% dropout rate - hypothetical metric)
- Students with tight deadlines give up
- Overwhelming 15+ fields for basic use cases

**Solution**: Three-level progressive creation
- **Quick Draft** (5 min): Name + Definition only → This US
- **Ready** (20 min): + Relations + Examples
- **Expert** (45 min): + Full metadata + Validation

This US focuses on the Quick Draft mode.

---

## Acceptance Criteria

### Functional Requirements

#### 1. Form Fields

**Required Fields**:
- [ ] **Term Name** (max 100 characters)
  - Text input
  - Character counter (0/100)
  - Red required indicator (*)
  - Validation: Min 3 characters
  - Error message: "Ce champ est requis"

- [ ] **Definition** (max 500 characters)
  - Textarea (resizable vertically)
  - Character counter (0/500)
  - Red required indicator (*)
  - Validation: Min 50 characters
  - Error message: "Minimum 50 caractères (actuellement X)"
  - Helper text: "Une définition simple et précise (200-300 caractères recommandés)"

**Optional Fields**:
- [ ] **Domain** (max 100 characters)
  - Text input
  - "Optionnel" badge
  - Helper text: "Le champ disciplinaire principal (vous pourrez en ajouter d'autres plus tard)"

#### 2. Progress Indicator

- [ ] **Progress bar** (0-100%)
  - Calculation:
    - Name filled (≥3 chars): +40%
    - Definition filled (≥50 chars): +50%
    - Domain filled (≥1 char): +10%
  - Smooth animated transition (300ms)
  - Blue gradient fill

- [ ] **"Mode Rapide" badge**
  - Icon: Lightning bolt ⚡
  - Text: "Mode Rapide"
  - Color: Primary blue background, white text

#### 3. Auto-Save Functionality

- [ ] **Auto-save to localStorage**:
  - Triggers 1 second after last keystroke
  - Visual feedback: "Sauvegarde..." → "Sauvegardé ✓"
  - Status indicator in top-right header
  - Key: `lexikon-draft`
  - Clears on successful submission

- [ ] **Draft restoration**:
  - On page load, check localStorage
  - If draft exists, populate fields
  - Show toast: "Brouillon restauré"

#### 4. Real-Time Validation

- [ ] **Term Name**:
  - Red border if < 3 chars and user typed
  - Error message appears below field
  - No validation until user starts typing

- [ ] **Definition**:
  - Red border if < 50 chars and user typed
  - Error shows current count: "Minimum 50 caractères (actuellement 23)"
  - Character counter turns red when approaching limit (>450 chars)

- [ ] **Submit button "Créer le terme →"**:
  - Disabled (50% opacity) until both required fields valid
  - Primary style when enabled
  - Shows loading spinner on submission

#### 5. Actions

- [ ] **Primary CTA**: "Créer le terme →"
  - Disabled by default
  - Enabled when: name ≥3 chars AND definition ≥50 chars
  - POST to `/api/terms` on click
  - Success: Clear draft, show success toast, redirect to term view

- [ ] **Secondary Action**: "Enregistrer comme brouillon"
  - Ghost button style
  - Always enabled (even if form invalid)
  - Saves to localStorage + backend (if user authenticated)
  - Shows toast: "Brouillon enregistré"

- [ ] **Skip to Advanced link**:
  - Text link at bottom
  - "Besoin de plus de champs ? → Passer en mode Avancé"
  - Opens same term in advanced editor

#### 6. Info Banner

- [ ] **Blue info box** at top of form:
  - Icon: Info circle ℹ️
  - Title: "Mode création rapide (5 minutes)"
  - Text: "Seuls les champs essentiels sont requis. Vous pourrez enrichir le terme plus tard avec des relations, exemples, et validation experte."

### Non-Functional Requirements

- [ ] **Performance**:
  - Form renders in < 500ms
  - Auto-save completes in < 200ms
  - Character counters update in < 50ms (no lag)

- [ ] **Accessibility (WCAG AA)**:
  - All inputs have associated labels
  - Required indicator read as "obligatoire" by screen readers
  - Error messages have `role="alert"`
  - Focus states visible (2px blue ring)
  - Keyboard navigation: Tab, Shift+Tab, Enter to submit

- [ ] **Responsive Design**:
  - Desktop (1440px): Form max-width 800px, centered
  - Mobile (375px): Full-width, stack actions vertically, touch targets ≥44px

- [ ] **Analytics Tracking**:
  - Track time spent on page (start → submit)
  - Track form abandonment rate
  - Track field completion rates
  - Track auto-save usage
  - Event: `quick_draft_created`

---

## Technical Notes

### Components Used

- **Input** (existing: `src/lib/components/Input.svelte`)
  - Used for: Term Name, Domain
  - Props: `label`, `required`, `maxlength`, `showCharCounter`, `errorMessage`, `helperText`

- **Textarea** (to create: `src/lib/components/Textarea.svelte`)
  - Used for: Definition
  - Props: Same as Input + `rows` (default 5)

- **Button** (existing: `src/lib/components/Button.svelte`)
  - Variants: `primary`, `ghost`

- **Progress** (to create: `src/lib/components/Progress.svelte`)
  - Props: `value` (0-100), `showLabel`, `color`

- **Alert** (to create: `src/lib/components/Alert.svelte`)
  - Variant: `info`
  - Used for: Blue banner at top

### Data Model

```typescript
interface QuickDraftTerm {
  name: string;              // Required, 3-100 chars
  definition: string;        // Required, 50-500 chars
  domain?: string;           // Optional, max 100 chars
  level: 'quick-draft';      // Always this value for this mode
  status: 'draft';           // Initial status
  created_at: string;        // ISO timestamp
  created_by: string;        // User ID
}
```

### API Endpoints

#### POST `/api/terms`

**Request**:
```json
{
  "name": "Épistémologie",
  "definition": "Étude critique des sciences, destinée à déterminer leur origine logique, leur valeur et leur portée.",
  "domain": "Philosophie",
  "level": "quick-draft",
  "status": "draft"
}
```

**Response** (201 Created):
```json
{
  "id": "term-uuid-123",
  "name": "Épistémologie",
  "definition": "...",
  "domain": "Philosophie",
  "level": "quick-draft",
  "status": "draft",
  "created_at": "2025-11-14T10:45:00Z",
  "created_by": "user-uuid-456",
  "next_steps": {
    "add_relations": "/terms/term-uuid-123/relations",
    "upgrade_level": "/terms/term-uuid-123/edit?mode=ready"
  }
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "validation_failed",
  "fields": {
    "name": "Minimum 3 caractères requis",
    "definition": "Minimum 50 caractères requis"
  }
}
```

#### POST `/api/drafts` (for "Enregistrer comme brouillon")

**Request**:
```json
{
  "name": "Épist",
  "definition": "Étude...",
  "domain": "",
  "auto_saved": false
}
```

**Response** (200 OK):
```json
{
  "draft_id": "draft-uuid-789",
  "saved_at": "2025-11-14T10:44:30Z",
  "ttl": 604800  // 7 days in seconds
}
```

### State Management

**LocalStorage** (Auto-save):
```javascript
{
  "lexikon-draft": {
    "name": "Épistémologie",
    "definition": "Étude critique...",
    "domain": "Philosophie",
    "timestamp": "2025-11-14T10:44:00Z"
  }
}
```

**Svelte Store** (Form state):
```typescript
const formStore = writable({
  name: '',
  definition: '',
  domain: '',
  isValid: false,
  isSaving: false,
  lastSaved: null
});
```

### Validation Rules

**Client-side** (real-time):
- Name: 3-100 chars, alphanumeric + spaces + accents
- Definition: 50-500 chars
- Domain: 0-100 chars (optional)

**Server-side** (on submit):
- Same rules + duplicate name check
- Sanitize HTML (prevent XSS)
- Check user permissions (authenticated)

---

## Design Tokens Used

```css
/* Colors */
--color-primary-600: #2563eb;   /* Buttons, focus states */
--color-success-500: #10b981;   /* Auto-save "Sauvegardé" */
--color-error-500: #ef4444;     /* Validation errors */
--color-gray-300: #d1d5db;      /* Input borders */

/* Typography */
--text-2xl: 1.5rem;  /* Card title */
--text-base: 1rem;   /* Inputs, body text */
--text-sm: 0.875rem; /* Helper text, labels */

/* Spacing */
--space-6: 1.5rem;   /* Form group margins */
--space-8: 2rem;     /* Card padding */

/* Radius */
--radius-md: 0.375rem;  /* Inputs */
--radius-xl: 0.75rem;   /* Card */
```

---

## Edge Cases & Error Handling

| Scenario | Behavior |
|----------|----------|
| User types 500 chars then deletes to 49 | Show error: "Minimum 50 caractères" |
| Network failure on submit | Show error toast, keep form data, retry button |
| Draft expired (>7 days) | Clear localStorage, show info toast |
| User pastes 1000 chars into definition | Truncate to 500, show warning |
| User navigates away mid-form | Auto-save triggers, show "confirm leave" dialog |
| Duplicate term name | Server returns 409, show error: "Ce terme existe déjà" |
| User not authenticated | Save draft to localStorage only, prompt to sign in on submit |

---

## Test Cases

### Unit Tests

```javascript
describe('Quick Draft Form', () => {
  it('disables submit when fields invalid', () => {});
  it('enables submit when name ≥3 and definition ≥50', () => {});
  it('updates progress bar correctly', () => {});
  it('triggers auto-save 1s after last keystroke', () => {});
  it('restores draft from localStorage on mount', () => {});
  it('clears draft after successful submission', () => {});
  it('shows character counter near-limit warning', () => {});
  it('validates minimum character requirements', () => {});
});
```

### E2E Tests

1. **Happy Path**:
   - Fill name: "Ontologie"
   - Fill definition: "Étude de l'être en tant qu'être, indépendamment de ses déterminations particulières." (90 chars)
   - Verify progress bar = 90%
   - Click "Créer le terme"
   - Verify redirect to term view

2. **Auto-Save Flow**:
   - Type in fields
   - Wait 1 second
   - Verify "Sauvegarde..." → "Sauvegardé"
   - Refresh page
   - Verify fields restored

3. **Validation Errors**:
   - Type "On" (2 chars)
   - Tab away
   - Verify error appears
   - Type "Ontologie"
   - Verify error disappears

4. **Draft Save**:
   - Partially fill form
   - Click "Enregistrer comme brouillon"
   - Verify toast appears
   - Verify draft saved to backend

---

## Definition of Done

- [ ] Code implemented and merged to `main`
- [ ] Unit tests passing (> 85% coverage)
- [ ] E2E tests passing (happy path + auto-save + validation)
- [ ] Accessibility audit passed (WCAG AA)
- [ ] Performance benchmarks met (< 500ms render, < 50ms input lag)
- [ ] Cross-browser tested (Chrome, Firefox, Safari, Edge)
- [ ] Mobile tested (iOS Safari, Android Chrome)
- [ ] Analytics events firing correctly
- [ ] API endpoints documented in OpenAPI spec
- [ ] Design review approved
- [ ] Code review approved by 2 developers
- [ ] User testing with 5 students (target persona)

---

## Success Metrics

**Target Metrics** (measure after 2 weeks in production):
- Average completion time: **< 5 minutes** (vs. 60 min baseline)
- Form abandonment rate: **< 15%** (vs. 52% baseline)
- Auto-save usage: **> 70%** of users trigger auto-save
- Quick Draft → Ready upgrade rate: **> 40%** (users enrich later)

---

## Dependencies

- **Requires**:
  - US-001 completed (adoption level determines if Quick Draft shown first)
  - Input component ready
  - Textarea component (to create)
  - Progress component (to create)
  - Alert component (to create)
  - Backend `/api/terms` endpoint

- **Blocks**:
  - US-003 (AI Relation Suggestions) - needs term ID
  - US-006 (Term View) - needs created term

---

## Open Questions

- [ ] Should we allow saving without minimum 50 chars as draft? (Current: yes, via "Enregistrer comme brouillon")
- [ ] Should we suggest definitions based on name (AI autocomplete)? (Future enhancement)
- [ ] What happens to orphaned drafts (never submitted)? (Auto-delete after 30 days)

---

## References

- **UX Analysis**: `docs/analyses/analyse-ux-parcours-critiques-v03.md` (Friction #1)
- **Wireframe**: `wireframes/02-creation-quick-draft.html`
- **Design System**: `docs/design/design-tokens.css`
- **Components**: `Input.svelte`, `Button.svelte`, (create: `Textarea.svelte`, `Progress.svelte`, `Alert.svelte`)

---

**Created**: 2025-11-14
**Last Updated**: 2025-11-14
**Status**: Ready for Development

---

## Appendix: Progressive Enhancement Plan

This Quick Draft is Level 1 of 3:

**Level 1: Quick Draft (this US)** - 5 min
- Fields: Name, Definition, Domain (optional)
- Status: `draft`
- Tier: Free (unlimited)

**Level 2: Ready** (future US-007) - 20 min
- + Relations (≥3 required)
- + Examples (≥1 required)
- + Synonyms
- Status: `ready`
- Tier: Free or Pro

**Level 3: Expert** (future US-008) - 45 min
- + Full metadata (author, sources, dates)
- + Expert validation request
- + Citation (DOI)
- Status: `validated` (after review)
- Tier: Pro required

Users can upgrade from Quick → Ready → Expert anytime.
