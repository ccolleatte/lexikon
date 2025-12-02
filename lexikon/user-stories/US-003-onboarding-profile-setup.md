# US-003: Onboarding - Configuration du Profil

**Epic**: Onboarding & First-Time User Experience
**Priority**: P0 (Critical - Must Have)
**Story Points**: 3
**Sprint**: 1
**Related Wireframe**: `wireframes/03-onboarding-profile-setup.html`

---

## User Story

**As a** new user who just selected my adoption level
**I want to** complete my user profile with personal and professional information
**So that** Lexikon can personalize my experience and provide relevant AI suggestions

---

## Context & Problem

**UX Analysis Reference**: Onboarding Flow (Multi-Step)

After selecting their adoption level (US-001), users need to provide basic profile information to:
- Enable personalized AI suggestions (domain-specific terminology)
- Set language and localization preferences
- Build trust through professional context (institution, domain)
- Enable collaboration features (name, email for validation requests)

**This is Step 2 of a 3-step onboarding**:
1. ✅ Adoption Level Selection (US-001)
2. **→ Profile Setup (this US)**
3. Preferences Configuration (LLM settings, notifications)

---

## Acceptance Criteria

### Functional Requirements

#### 1. Progress Stepper

- [ ] **3-step stepper displayed** at top of page
  - Step 1: "Adoption" (completed, green checkmark)
  - Step 2: "Profil" (active, blue, number "2")
  - Step 3: "Préférences" (pending, gray, number "3")

- [ ] **Visual indicators**:
  - Completed steps: Green background, checkmark icon
  - Active step: Blue background, white number, pulsing ring
  - Pending steps: Gray background, gray number
  - Connectors: Green (completed) or gray (pending)

#### 2. Selected Level Badge

- [ ] **Display selected adoption level** from US-001
  - Icon + text: "🚀 Niveau sélectionné : Projet Rapide"
  - Blue background (primary-500 10% opacity)
  - Positioned below stepper, centered

#### 3. Form Fields

**Required Fields**:

- [ ] **Prénom** (First Name)
  - Text input
  - Required indicator (red *)
  - Validation: Min 2 characters
  - Error: "Ce champ est requis"

- [ ] **Nom** (Last Name)
  - Text input
  - Required indicator (red *)
  - Validation: Min 2 characters
  - Error: "Ce champ est requis"

- [ ] **Email**
  - Email input type
  - Required indicator (red *)
  - Validation: Valid email format (regex)
  - Helper text: "Nous utiliserons cette adresse pour les notifications importantes"
  - Error: "Veuillez entrer une adresse email valide"

**Optional Fields**:

- [ ] **Photo de profil** (Avatar)
  - File upload with preview
  - "Optionnel" badge
  - Drag & drop or click to browse
  - Accepted formats: JPG, PNG, GIF
  - Max size: 2MB
  - Default: Generic user icon emoji (👤)
  - Preview updates on file selection

- [ ] **Institution**
  - Text input
  - "Optionnel" badge
  - Placeholder: "Université Paris-Sorbonne"
  - Helper text: "Université, entreprise, ou organisme"

- [ ] **Domaine principal** (Primary Domain)
  - Select dropdown
  - "Optionnel" badge
  - Options:
    - Philosophie
    - Sciences de l'éducation
    - Sociologie
    - Psychologie
    - Linguistique
    - Histoire
    - Informatique
    - Data Science
    - Autre
  - Helper text: "Pour de meilleures suggestions AI"

- [ ] **Langue préférée** (Preferred Language)
  - Select dropdown
  - Default: French (based on browser locale)
  - Options: Français, English, Español, Deutsch, Italiano
  - No helper text

- [ ] **Pays** (Country)
  - Select dropdown
  - "Optionnel" badge
  - Options: France, Belgique, Suisse, Canada, États-Unis, Royaume-Uni, Allemagne, Espagne, Italie
  - No helper text

#### 4. Real-Time Validation

- [ ] **First Name**:
  - No validation until user types
  - If < 2 chars after typing: Red border + error message
  - Error disappears when ≥ 2 chars

- [ ] **Last Name**:
  - Same validation as first name

- [ ] **Email**:
  - No validation until user types
  - If invalid format: Red border + error message
  - Regex: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`

- [ ] **Submit button "Continuer →"**:
  - Disabled (50% opacity) until all required fields valid
  - Enabled when: firstName ≥2 AND lastName ≥2 AND email valid

#### 5. Actions

- [ ] **"← Précédent" button** (ghost variant):
  - Always enabled
  - Navigates back to adoption level selection (US-001)
  - Preserves current form data in localStorage

- [ ] **"Continuer →" button** (primary variant):
  - Disabled by default
  - Enabled when all required fields valid
  - POST to `/api/users/profile` on click
  - Success: Navigate to preferences step

#### 6. Data Persistence

- [ ] **Pre-populate email** if provided by authentication:
  - Check URL params: `?email=user@example.com`
  - Auto-fill email field
  - Run validation

- [ ] **Save draft on navigation back**:
  - Store form data in localStorage (`lexikon-onboarding-profile`)
  - Restore on return from previous step

### Non-Functional Requirements

- [ ] **Performance**:
  - Page loads in < 800ms
  - Form interactions respond in < 100ms
  - Avatar preview updates in < 300ms

- [ ] **Accessibility (WCAG AA)**:
  - All inputs have associated labels
  - Required fields announced by screen readers
  - Stepper has proper ARIA landmarks
  - Keyboard navigation: Tab through all fields, Enter to submit
  - Focus states visible (2px blue ring)
  - Error messages have `role="alert"`

- [ ] **Responsive Design**:
  - Desktop (1440px): Two-column form row (first name | last name)
  - Tablet (768px): Single column
  - Mobile (375px): Single column, avatar upload stacked vertically

- [ ] **Analytics Tracking**:
  - Track form abandonment (which fields completed)
  - Track completion time
  - Track optional field completion rates
  - Event: `onboarding_profile_completed`

---

## Technical Notes

### Components Used

- **Input** (`src/lib/components/Input.svelte`)
  - Used for: Prénom, Nom, Email, Institution
  - Props: `label`, `required`, `errorMessage`, `helperText`, `type`

- **Select** (`src/lib/components/Select.svelte`)
  - Used for: Domaine, Langue, Pays
  - Props: `label`, `options`, `placeholder`, `helperText`

- **Button** (`src/lib/components/Button.svelte`)
  - Variants: `primary` (Continuer), `ghost` (Précédent)

- **AvatarUpload** (to create: `src/lib/components/AvatarUpload.svelte`)
  - Custom component for avatar upload with preview
  - Props: `maxSize`, `acceptedFormats`, `value`
  - Events: `onChange`

- **Stepper** (to create: `src/lib/components/Stepper.svelte`)
  - Custom component for multi-step progress
  - Props: `steps`, `currentStep`

### Data Model

```typescript
interface UserProfile {
  // Required
  firstName: string;      // Min 2 chars
  lastName: string;       // Min 2 chars
  email: string;          // Valid email format

  // Optional
  avatar?: string;        // Base64 or upload URL
  institution?: string;   // Max 200 chars
  primaryDomain?: string; // Enum: see options above
  language: string;       // Default: 'fr', options: fr, en, es, de, it
  country?: string;       // ISO country code

  // Metadata (set by system)
  adoptionLevel: 'quick-project' | 'research-project' | 'production-api'; // From US-001
  createdAt: string;      // ISO timestamp
  updatedAt: string;      // ISO timestamp
}
```

### API Endpoints

#### POST `/api/users/profile`

**Request**:
```json
{
  "firstName": "Marie",
  "lastName": "Dupont",
  "email": "marie.dupont@universite.fr",
  "avatar": "data:image/png;base64,...",
  "institution": "Université Paris-Sorbonne",
  "primaryDomain": "philosophie",
  "language": "fr",
  "country": "FR",
  "adoptionLevel": "quick-project"
}
```

**Response** (201 Created):
```json
{
  "id": "user-uuid-123",
  "firstName": "Marie",
  "lastName": "Dupont",
  "email": "marie.dupont@universite.fr",
  "avatar": "https://cdn.lexikon.app/avatars/user-uuid-123.jpg",
  "institution": "Université Paris-Sorbonne",
  "primaryDomain": "philosophie",
  "language": "fr",
  "country": "FR",
  "adoptionLevel": "quick-project",
  "createdAt": "2025-11-14T11:00:00Z",
  "nextStep": "/onboarding/preferences"
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "validation_failed",
  "fields": {
    "email": "Email déjà utilisé",
    "firstName": "Minimum 2 caractères requis"
  }
}
```

#### POST `/api/users/avatar` (separate endpoint for large files)

**Request**: `multipart/form-data`
```
avatar: File (image/jpeg, image/png, image/gif)
```

**Response** (200 OK):
```json
{
  "avatarUrl": "https://cdn.lexikon.app/avatars/user-uuid-123.jpg"
}
```

### State Management

**LocalStorage** (Draft persistence):
```javascript
{
  "lexikon-onboarding-profile": {
    "firstName": "Marie",
    "lastName": "Dupont",
    "email": "marie.dupont@universite.fr",
    "institution": "Université Paris-Sorbonne",
    "primaryDomain": "philosophie",
    "language": "fr",
    "country": "FR",
    "timestamp": "2025-11-14T10:58:00Z"
  }
}
```

**Svelte Store** (Form state):
```typescript
const profileStore = writable({
  firstName: '',
  lastName: '',
  email: '',
  avatar: null,
  institution: '',
  primaryDomain: '',
  language: 'fr',
  country: '',
  isValid: false,
  errors: {}
});
```

### Validation Rules

**Client-side**:
- First Name: 2-100 chars, letters + spaces + hyphens + accents
- Last Name: 2-100 chars, same rules
- Email: Valid format `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`
- Avatar: Max 2MB, formats: JPG, PNG, GIF
- Institution: Max 200 chars
- Primary Domain: Must be from predefined list
- Language: Must be from predefined list
- Country: Must be from predefined list (ISO codes)

**Server-side**:
- All client-side rules +
- Email uniqueness check
- Avatar virus scan (if uploaded)
- Sanitize all text inputs (prevent XSS)

---

## Design Tokens Used

```css
/* Stepper colors */
--color-success-500: #10b981;  /* Completed step */
--color-primary-600: #2563eb;  /* Active step */
--color-gray-200: #e5e7eb;     /* Pending step, connectors */

/* Form elements */
--color-gray-300: #d1d5db;     /* Input borders */
--color-error-500: #ef4444;    /* Validation errors */

/* Avatar upload */
--color-gray-50: #f9fafb;      /* Upload area background */
--color-primary-500: #3b82f6;  /* Upload area hover border */

/* Spacing */
--space-4: 1rem;   /* Default gaps */
--space-6: 1.5rem; /* Card padding */
--space-8: 2rem;   /* Section margins */
```

---

## Edge Cases & Error Handling

| Scenario | Behavior |
|----------|----------|
| Email already exists | Server returns 400, show error: "Cette adresse email est déjà utilisée" |
| Avatar too large (>2MB) | Show error toast, prevent upload |
| Invalid image format | Show error toast: "Format non supporté. Utilisez JPG, PNG ou GIF" |
| Network failure on submit | Show error toast, keep form data, add retry button |
| User navigates back | Save form to localStorage, restore on return |
| User refreshes page | Restore from localStorage if exists |
| No adoption level in context | Redirect to step 1 (US-001) |
| Email pre-filled from auth | Auto-populate, mark as valid if correct format |

---

## Test Cases

### Unit Tests

```javascript
describe('Profile Setup Form', () => {
  it('disables submit when required fields empty', () => {});
  it('enables submit when all required fields valid', () => {});
  it('validates email format correctly', () => {});
  it('validates first/last name min length', () => {});
  it('allows submission with only required fields', () => {});
  it('uploads and previews avatar correctly', () => {});
  it('rejects avatar larger than 2MB', () => {});
  it('saves draft to localStorage on navigation', () => {});
  it('restores draft from localStorage on mount', () => {});
});
```

### E2E Tests

1. **Happy Path (Required Fields Only)**:
   - Navigate from US-001 with adoption level
   - Fill: Marie, Dupont, marie@test.fr
   - Click "Continuer"
   - Verify POST to API
   - Verify redirect to preferences

2. **Happy Path (All Fields)**:
   - Fill all fields including optional
   - Upload avatar
   - Verify avatar preview updates
   - Submit
   - Verify all data sent to API

3. **Validation Errors**:
   - Type "M" in first name
   - Tab away
   - Verify error appears
   - Type "Marie"
   - Verify error disappears

4. **Navigation Back**:
   - Partially fill form
   - Click "← Précédent"
   - Navigate forward again
   - Verify form data restored

5. **Avatar Upload**:
   - Click "Parcourir"
   - Select 3MB image
   - Verify error: "Le fichier doit faire moins de 2MB"
   - Select 500KB image
   - Verify preview updates

---

## Definition of Done

- [ ] Code implemented and merged to `main`
- [ ] Unit tests passing (> 80% coverage)
- [ ] E2E tests passing (happy path + validation + navigation)
- [ ] Accessibility audit passed (WCAG AA)
- [ ] Stepper component created and functional
- [ ] Avatar upload with preview working
- [ ] Cross-browser tested (Chrome, Firefox, Safari)
- [ ] Mobile tested (iOS, Android)
- [ ] API endpoint `/api/users/profile` implemented
- [ ] Analytics events firing correctly
- [ ] Design review approved
- [ ] Code review approved by 2 developers

---

## Success Metrics

**Target Metrics** (measure after 2 weeks):
- Form completion rate: **> 85%** (vs. baseline TBD)
- Average completion time: **< 90 seconds**
- Optional field completion rates:
  - Institution: **> 60%**
  - Primary Domain: **> 70%** (important for AI)
  - Avatar: **> 30%**
- Validation error rate: **< 10%** (good defaults, clear labels)

---

## Dependencies

- **Requires**:
  - US-001 completed (adoption level must be selected first)
  - Input component ready
  - Select component ready
  - Button component ready

- **Creates**:
  - Stepper component (new)
  - AvatarUpload component (new)

- **Blocks**:
  - US-004 (Preferences Setup) - needs user profile created
  - US-002 (Quick Draft) - needs primaryDomain for AI suggestions

---

## Open Questions

- [ ] Should we allow Google/GitHub OAuth to pre-fill profile? (Future enhancement)
- [ ] Should institution be free text or autocomplete from database? (Current: free text, future: autocomplete)
- [ ] Should we verify email before allowing to proceed? (Current: no, verify later via email)

---

## References

- **Wireframe**: `wireframes/03-onboarding-profile-setup.html`
- **Design System**: `docs/design/design-tokens.css`
- **Components**: `Input.svelte`, `Select.svelte`, `Button.svelte`, (create: `Stepper.svelte`, `AvatarUpload.svelte`)
- **Previous Step**: US-001 (Adoption Level Selection)
- **Next Step**: US-004 (Preferences Configuration - to be written)

---

**Created**: 2025-11-14
**Last Updated**: 2025-11-14
**Status**: Ready for Development
