# 🚀 Developer Handoff Guide - Lexikon v0.1

**Version**: 0.1.0
**Date**: 2025-11-14
**Sprint**: Pre-Development → Sprint 1
**UX Designer**: Claude
**Target Audience**: Frontend Developers, Full-Stack Engineers

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start (30 minutes)](#quick-start-30-minutes)
3. [Design System Setup](#design-system-setup)
4. [Component Library](#component-library)
5. [Wireframes & Flows](#wireframes--flows)
6. [User Stories](#user-stories)
7. [Implementation Priority](#implementation-priority)
8. [Quality Checklist](#quality-checklist)
9. [FAQ & Troubleshooting](#faq--troubleshooting)

---

## Overview

### What You're Building

**Lexikon v0.1** - A generic lexical ontology service that allows academics and professionals to create, validate, and manage ontologies with AI assistance.

**Key Differentiators**:
- **LLM-agnostic**: Users can bring their own API keys (BYOK) or use our free tier
- **Differentiated onboarding**: 3 adoption levels (Quick Project, Research, Production)
- **Progressive creation**: 5-minute Quick Draft → 20-minute Ready → 45-minute Expert
- **Human-in-the-loop**: Mandatory validation for all AI suggestions

### What's Been Delivered

```
✅ Design Tokens (3 formats: CSS, JSON, Tailwind)
✅ 3 Production-Ready Components (Button, Input, Textarea)
✅ 2 High-Fidelity Wireframes (HTML)
✅ 2 Detailed User Stories (US-001, US-002)
✅ Icons Library (30 Lucide icons)
✅ Comprehensive Documentation
```

### Tech Stack

- **Framework**: SvelteKit 2.x
- **Styling**: TailwindCSS 3.x + CSS Custom Properties
- **Icons**: Lucide Svelte
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL + Neo4j (graph)
- **TypeScript**: For type safety

---

## Quick Start (30 minutes)

### Step 1: Environment Setup (10 min)

```bash
# Clone repository (if not already)
cd /home/user/lexikon

# Install dependencies
npm install

# Install Lucide icons
npm install lucide-svelte

# Start dev server
npm run dev -- --open
```

### Step 2: Import Design Tokens (5 min)

**Option A: Tailwind (Recommended)**

```javascript
// tailwind.config.js
import tokens from './docs/design/tailwind.config.js';

export default {
  ...tokens,
  content: [
    './src/**/*.{html,js,svelte,ts}'
  ]
};
```

**Option B: CSS Variables**

```css
/* src/app.css */
@import '../docs/design/design-tokens.css';
```

**Option C: Programmatic (JSON)**

```typescript
// src/lib/theme.ts
import tokens from '../docs/design/design-tokens.json';

export const colors = tokens.colors;
export const spacing = tokens.spacing;
```

### Step 3: Test Components (10 min)

```svelte
<!-- src/routes/+page.svelte -->
<script>
  import Button from '$lib/components/Button.svelte';
  import Input from '$lib/components/Input.svelte';
</script>

<div class="p-8">
  <Input
    label="Test Input"
    placeholder="Type here..."
    helperText="This is a helper text"
    showCharCounter
    maxlength={100}
  />

  <Button variant="primary" on:click={() => alert('Works!')}>
    Click Me
  </Button>
</div>
```

**Expected Result**: Input field with label, char counter, and a primary blue button.

### Step 4: View Wireframes (5 min)

```bash
# Open in browser
open wireframes/01-onboarding-adoption-level.html
open wireframes/02-creation-quick-draft.html
```

**Inspect**: Hover states, interactions, responsive behavior.

---

## Design System Setup

### Colors

#### Primary Palette (Academic Blue)

```css
--color-primary-500: #3b82f6;  /* Base - bright blue */
--color-primary-600: #2563eb;  /* Default state - CTAs */
--color-primary-700: #1d4ed8;  /* Active/pressed */
```

**Usage**:
- Primary CTAs (buttons, links)
- Focus states
- Selected items

#### Semantic Colors

```css
/* Success */
--color-success-500: #10b981;  /* Validation passed, saved */

/* Error */
--color-error-500: #ef4444;    /* Form errors, required fields */

/* Warning */
--color-warning-500: #eab308;  /* Caution, draft status */
```

#### Lexikon-Specific Colors

```css
/* Relation Types (for graph visualizations) */
--color-relation-isa: #3b82f6;        /* is_a - Blue */
--color-relation-partof: #8b5cf6;     /* part_of - Violet */
--color-relation-employs: #10b981;    /* employs - Green */

/* Term Status */
--color-status-draft: #9ca3af;        /* Gray */
--color-status-validated: #10b981;    /* Green */
--color-status-review: #3b82f6;       /* Blue */
```

**Usage Example**:

```svelte
<span class="bg-status-validated text-white px-3 py-1 rounded-full">
  Validé
</span>
```

### Typography

#### Font Families

```css
--font-sans: 'Inter', system-ui, sans-serif;      /* UI text */
--font-mono: 'JetBrains Mono', monospace;         /* Code, IDs */
--font-serif: 'Merriweather', Georgia, serif;     /* Long-form content */
```

**Setup** (add to `app.html`):

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

#### Font Sizes (Perfect Fourth Scale 1.25)

```css
--text-xs: 0.75rem;    /* 12px - helper text, badges */
--text-sm: 0.875rem;   /* 14px - labels, secondary text */
--text-base: 1rem;     /* 16px - body text, inputs */
--text-lg: 1.125rem;   /* 18px - subtitles */
--text-xl: 1.25rem;    /* 20px - card titles */
--text-2xl: 1.5rem;    /* 24px - page titles */
--text-3xl: 1.875rem;  /* 30px - hero titles */
```

**Usage Example**:

```svelte
<h1 class="text-2xl font-semibold text-gray-900">
  Création de terme
</h1>
```

### Spacing (Base 4px)

```css
--space-4: 1rem;    /* 16px - Base unit, default padding */
--space-6: 1.5rem;  /* 24px - Card padding, section spacing */
--space-8: 2rem;    /* 32px - Large sections */
```

**8px Grid System**:
- All spacing should be multiples of 4px (0.25rem)
- Prefer semantic tokens: `--space-md` (16px), `--space-lg` (24px)

### Border Radius

```css
--radius-md: 0.375rem;  /* 6px - Inputs, buttons */
--radius-lg: 0.5rem;    /* 8px - Cards */
--radius-xl: 0.75rem;   /* 12px - Modals */
--radius-full: 9999px;  /* Circular - badges, avatars */
```

### Shadows & Elevation

```css
--shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1);   /* Cards */
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1); /* Hover state */
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1); /* Modals */
```

**Component Defaults**:
- Cards: `--shadow-sm`
- Modals: `--shadow-lg`
- Popovers: `--shadow-md`

---

## Component Library

### Button (`Button.svelte`)

**Location**: `src/lib/components/Button.svelte`

#### Props

```typescript
variant: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' = 'primary';
size: 'sm' | 'md' | 'lg' = 'md';
disabled: boolean = false;
loading: boolean = false;
fullWidth: boolean = false;
type: 'button' | 'submit' | 'reset' = 'button';
href: string | undefined = undefined;
className: string = '';
```

#### Usage Examples

```svelte
<!-- Primary CTA -->
<Button variant="primary" on:click={handleSubmit}>
  Créer le terme →
</Button>

<!-- Secondary action -->
<Button variant="ghost">
  Annuler
</Button>

<!-- Loading state -->
<Button variant="primary" loading={isSubmitting}>
  Enregistrement...
</Button>

<!-- Link as button -->
<Button href="/dashboard" variant="outline">
  Retour
</Button>

<!-- Small size -->
<Button size="sm" variant="secondary">
  Modifier
</Button>
```

#### Accessibility

- ✅ Keyboard navigation (Tab, Enter, Space)
- ✅ Focus ring (2px blue, 2px offset)
- ✅ Disabled state (cursor: not-allowed, opacity 50%)
- ✅ Loading spinner with animation

---

### Input (`Input.svelte`)

**Location**: `src/lib/components/Input.svelte`

#### Props

```typescript
type: 'text' | 'email' | 'password' | 'number' | 'url' = 'text';
value: string | number = '';
placeholder: string = '';
label: string = '';
helperText: string = '';
errorMessage: string = '';
disabled: boolean = false;
required: boolean = false;
readonly: boolean = false;
maxlength: number | undefined = undefined;
showCharCounter: boolean = false;
id: string = auto-generated;
name: string = '';
```

#### Usage Examples

```svelte
<!-- Basic input -->
<Input
  label="Nom du terme"
  placeholder="Ex: Épistémologie"
  bind:value={termName}
  required
/>

<!-- With character counter -->
<Input
  label="Titre"
  maxlength={100}
  showCharCounter
  bind:value={title}
/>

<!-- Email with validation -->
<Input
  type="email"
  label="Email"
  errorMessage={emailError}
  helperText="Nous ne partagerons jamais votre email"
  bind:value={email}
/>

<!-- Disabled state -->
<Input
  label="ID du terme"
  value={termId}
  disabled
  readonly
/>
```

#### Events

```svelte
<Input
  on:input={(e) => console.log('Input:', e.detail.value)}
  on:change={(e) => console.log('Changed:', e.detail.value)}
  on:focus={() => console.log('Focused')}
  on:blur={() => validateField()}
/>
```

#### Validation Pattern

```svelte
<script>
  let termName = '';
  let nameError = '';

  function validateName() {
    if (termName.length < 3) {
      nameError = 'Minimum 3 caractères requis';
    } else {
      nameError = '';
    }
  }
</script>

<Input
  label="Nom"
  bind:value={termName}
  errorMessage={nameError}
  on:blur={validateName}
  required
/>
```

---

### Textarea (`Textarea.svelte`)

**Location**: `src/lib/components/Textarea.svelte`

#### Props

```typescript
value: string = '';
label: string = '';
helperText: string = '';
errorMessage: string = '';
placeholder: string = '';
required: boolean = false;
disabled: boolean = false;
readonly: boolean = false;
maxlength: number | undefined = undefined;
showCharCounter: boolean = false;
rows: number = 5;
resize: 'none' | 'vertical' | 'horizontal' | 'both' = 'vertical';
autoResize: boolean = false;
```

#### Usage Examples

```svelte
<!-- Definition field with counter -->
<Textarea
  label="Définition"
  placeholder="Définissez le terme de manière claire..."
  maxlength={500}
  showCharCounter
  helperText="Une définition simple et précise (200-300 caractères recommandés)"
  bind:value={definition}
  required
/>

<!-- Auto-resize textarea -->
<Textarea
  label="Notes"
  autoResize
  placeholder="Vos notes..."
  bind:value={notes}
/>

<!-- Validation -->
<Textarea
  label="Description"
  errorMessage={descError}
  on:blur={validateDescription}
  bind:value={description}
/>
```

---

## Wireframes & Flows

### 01 - Onboarding: Adoption Level Selection

**File**: `wireframes/01-onboarding-adoption-level.html`
**User Story**: `user-stories/US-001-onboarding-adoption-level.md`

#### What to Implement

1. **3 Radio Cards**:
   - Quick Project (student icon 🚀)
   - Research Project (academic icon 🎓)
   - Production API (developer icon ⚡)

2. **Each Card Contains**:
   - Icon (40×40px)
   - Title (font-size: 1.25rem, font-weight: 600)
   - Subtitle (font-size: 0.875rem, gray-600)
   - User quote (italic, gray-700)
   - 3 feature bullets (→ arrow prefix, primary-500)
   - Pricing badge (rounded-full, color-coded)

3. **Interactions**:
   - Hover: Border → primary-500, shadow-md, translateY(-2px)
   - Selected: Left border 4px blue, radio filled
   - CTA enabled only when selected

#### Implementation Notes

**SvelteKit Route**: `src/routes/onboarding/+page.svelte`

```svelte
<script lang="ts">
  import Button from '$lib/components/Button.svelte';

  let selectedLevel: string | null = null;

  const levels = [
    {
      id: 'quick-project',
      icon: '🚀',
      title: 'Projet Rapide',
      subtitle: 'Étudiant, usage ponctuel',
      quote: "J'ai besoin d'une ontologie pour mon mémoire",
      features: [
        'Setup en 30 minutes',
        'Export quand terminé',
        'Gratuit, pas de validation obligatoire'
      ],
      badge: { text: 'Gratuit', type: 'free' }
    },
    // ... other levels
  ];

  function handleContinue() {
    if (selectedLevel) {
      // Store in user profile
      goto(`/onboarding/profile?level=${selectedLevel}`);
    }
  }
</script>

{#each levels as level}
  <label class="radio-card" class:selected={selectedLevel === level.id}>
    <input
      type="radio"
      name="adoption-level"
      value={level.id}
      bind:group={selectedLevel}
    />
    <!-- Card content -->
  </label>
{/each}

<Button
  variant="primary"
  disabled={!selectedLevel}
  on:click={handleContinue}
>
  Continuer →
</Button>
```

**CSS** (use design tokens):

```css
.radio-card {
  border: 2px solid var(--color-gray-200);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  cursor: pointer;
  transition: all 0.2s;
}

.radio-card:hover {
  border-color: var(--color-primary-500);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.radio-card.selected {
  border-left: 4px solid var(--color-primary-600);
  padding-left: calc(var(--space-6) - 4px);
}
```

---

### 02 - Quick Draft: Term Creation

**File**: `wireframes/02-creation-quick-draft.html`
**User Story**: `user-stories/US-002-quick-draft-creation.md`

#### What to Implement

1. **Auto-Save Header**:
   - Status indicator (top-right)
   - "Sauvegardé ✓" (green) / "Sauvegarde..." (gray)

2. **Progress Bar**:
   - Title: "Création de terme"
   - Badge: "Mode Rapide ⚡"
   - Progress: 0-100% (animated)

3. **Info Banner**:
   - Blue background (primary-500 10% opacity)
   - Icon: Info circle
   - Text: "Mode création rapide (5 minutes)..."

4. **Form Fields**:
   - Term Name (Input, required, max 100)
   - Definition (Textarea, required, max 500)
   - Domain (Input, optional, max 100)

5. **Actions**:
   - Primary: "Créer le terme →" (disabled until valid)
   - Secondary: "Enregistrer comme brouillon" (always enabled)
   - Link: "Passer en mode Avancé"

#### Implementation Notes

**SvelteKit Route**: `src/routes/terms/new/+page.svelte`

```svelte
<script lang="ts">
  import Input from '$lib/components/Input.svelte';
  import Textarea from '$lib/components/Textarea.svelte';
  import Button from '$lib/components/Button.svelte';
  import { browser } from '$app/environment';

  let termName = '';
  let definition = '';
  let domain = '';

  let nameError = '';
  let defError = '';
  let autoSaveStatus = 'saved';

  // Progress calculation
  $: progress = calculateProgress(termName, definition, domain);

  function calculateProgress(name: string, def: string, dom: string): number {
    let p = 0;
    if (name.length >= 3) p += 40;
    if (def.length >= 50) p += 50;
    if (dom.length > 0) p += 10;
    return p;
  }

  // Validation
  $: isValid = termName.length >= 3 && definition.length >= 50;

  // Auto-save to localStorage
  let autoSaveTimeout: ReturnType<typeof setTimeout>;
  function autoSave() {
    if (!browser) return;

    clearTimeout(autoSaveTimeout);
    autoSaveStatus = 'saving';

    autoSaveTimeout = setTimeout(() => {
      const draft = { termName, definition, domain, timestamp: new Date().toISOString() };
      localStorage.setItem('lexikon-draft', JSON.stringify(draft));
      autoSaveStatus = 'saved';
    }, 1000);
  }

  $: if (browser && (termName || definition || domain)) {
    autoSave();
  }

  // Restore draft on mount
  import { onMount } from 'svelte';
  onMount(() => {
    const draft = localStorage.getItem('lexikon-draft');
    if (draft) {
      const data = JSON.parse(draft);
      termName = data.termName || '';
      definition = data.definition || '';
      domain = data.domain || '';
    }
  });

  // Validation functions
  function validateName() {
    if (termName.length > 0 && termName.length < 3) {
      nameError = 'Minimum 3 caractères requis';
    } else {
      nameError = '';
    }
  }

  function validateDefinition() {
    if (definition.length > 0 && definition.length < 50) {
      defError = `Minimum 50 caractères (actuellement ${definition.length})`;
    } else {
      defError = '';
    }
  }

  // Submit
  async function handleSubmit() {
    // POST to API
    const response = await fetch('/api/terms', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: termName,
        definition,
        domain,
        level: 'quick-draft',
        status: 'draft'
      })
    });

    if (response.ok) {
      const term = await response.json();
      localStorage.removeItem('lexikon-draft');
      goto(`/terms/${term.id}`);
    }
  }
</script>

<!-- Header with auto-save status -->
<header class="app-header">
  <div class="logo">LEXIKON</div>
  <div class="auto-save-status" class:saving={autoSaveStatus === 'saving'}>
    {autoSaveStatus === 'saved' ? '✓ Sauvegardé' : 'Sauvegarde...'}
  </div>
</header>

<!-- Progress bar -->
<div class="progress-section">
  <div class="progress-header">
    <h2>Création de terme</h2>
    <span class="badge">⚡ Mode Rapide</span>
  </div>
  <div class="progress-bar">
    <div class="progress-fill" style:width="{progress}%"></div>
  </div>
</div>

<!-- Info banner -->
<div class="info-banner">
  <svg><!-- Info icon --></svg>
  <div>
    <strong>Mode création rapide (5 minutes)</strong>
    <p>Seuls les champs essentiels sont requis...</p>
  </div>
</div>

<!-- Form -->
<form on:submit|preventDefault={handleSubmit}>
  <Input
    label="Nom du terme"
    bind:value={termName}
    placeholder="Ex: Épistémologie"
    maxlength={100}
    showCharCounter
    required
    errorMessage={nameError}
    helperText="Le nom principal de votre concept (évitez les abréviations)"
    on:blur={validateName}
  />

  <Textarea
    label="Définition"
    bind:value={definition}
    placeholder="Définissez le terme de manière claire..."
    maxlength={500}
    showCharCounter
    required
    errorMessage={defError}
    helperText="Une définition simple et précise (200-300 caractères recommandés)"
    on:blur={validateDefinition}
  />

  <Input
    label="Domaine"
    bind:value={domain}
    placeholder="Ex: Philosophie, Sciences de l'éducation..."
    maxlength={100}
    helperText="Le champ disciplinaire principal (vous pourrez en ajouter d'autres plus tard)"
  />

  <div class="actions">
    <Button type="submit" variant="primary" disabled={!isValid}>
      Créer le terme →
    </Button>
    <Button type="button" variant="ghost">
      Enregistrer comme brouillon
    </Button>
  </div>
</form>
```

---

## User Stories

### US-001: Onboarding - Adoption Level

**File**: `user-stories/US-001-onboarding-adoption-level.md`

**Key Acceptance Criteria**:
- [ ] 3 radio cards displayed
- [ ] Only one selectable at a time
- [ ] CTA "Continuer" enabled only when selection made
- [ ] Keyboard navigation functional
- [ ] Analytics tracking selection

**Technical Notes**:
- Store selection in localStorage (`lexikon-onboarding-level`)
- POST to `/api/onboarding/adoption-level` on continue
- Next route: `/onboarding/profile?level={selected}`

**Priority**: P0 (Must Have for Sprint 1)

---

### US-002: Quick Draft Creation

**File**: `user-stories/US-002-quick-draft-creation.md`

**Key Acceptance Criteria**:
- [ ] Auto-save to localStorage every 1 second
- [ ] Progress bar updates in real-time
- [ ] Validation: name ≥3 chars, definition ≥50 chars
- [ ] Submit disabled until valid
- [ ] Character counters turn red near limit

**Technical Notes**:
- POST to `/api/terms` on submit
- Auto-save key: `lexikon-draft`
- Clear draft on successful submission
- Track completion time (target: < 5 minutes)

**Priority**: P0 (Must Have for Sprint 1)

---

## Implementation Priority

### Sprint 1 (Weeks 1-2)

**Week 1: Onboarding Flow**

- [ ] **Day 1-2**: Setup project, install dependencies, configure Tailwind
- [ ] **Day 3**: Implement US-001 (Onboarding Adoption Level)
  - Create RadioCard component
  - Implement selection logic
  - Add analytics tracking
- [ ] **Day 4**: Create profile setup screen (not wireframed yet - basic form)
- [ ] **Day 5**: Testing, bug fixes, accessibility audit

**Week 2: Quick Draft Creation**

- [ ] **Day 1-2**: Implement US-002 (Quick Draft)
  - Form with Input, Textarea components
  - Auto-save functionality
  - Progress bar
- [ ] **Day 3**: API integration (`POST /api/terms`)
- [ ] **Day 4**: Validation, error handling
- [ ] **Day 5**: Testing, performance optimization

### Sprint 2 (Weeks 3-4)

**Future User Stories** (not yet detailed):
- US-003: AI Relation Suggestions
- US-004: Import Wizard (CSV/Excel mapping)
- US-005: Collaborative Validation
- US-006: LLM Configuration (BYOK)

---

## Quality Checklist

### Before Merging PR

#### Functional

- [ ] All acceptance criteria met (see user story)
- [ ] Form validation works correctly
- [ ] Error states display properly
- [ ] Success states work (toast, redirect)
- [ ] Analytics events fire correctly

#### Accessibility (WCAG AA)

- [ ] Keyboard navigation functional (Tab, Shift+Tab, Enter, Space)
- [ ] Focus states visible (2px ring, 2px offset)
- [ ] Color contrast ratio ≥ 4.5:1 for text
- [ ] All inputs have associated labels
- [ ] Error messages have `role="alert"`
- [ ] ARIA attributes correct (`aria-invalid`, `aria-describedby`)
- [ ] Screen reader tested (NVDA or VoiceOver)

#### Performance

- [ ] Page loads in < 1 second
- [ ] First Contentful Paint < 1.5s
- [ ] Interactive in < 2s
- [ ] No layout shifts (CLS < 0.1)
- [ ] Images optimized (WebP, lazy loading)

#### Cross-Browser

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

#### Responsive

- [ ] Mobile (375px - iPhone SE)
- [ ] Tablet (768px - iPad)
- [ ] Desktop (1440px)
- [ ] Touch targets ≥ 44px on mobile

#### Code Quality

- [ ] TypeScript types defined
- [ ] No console errors
- [ ] ESLint passing
- [ ] Unit tests passing (> 80% coverage)
- [ ] E2E tests passing (happy path)

---

## FAQ & Troubleshooting

### Design Tokens

**Q: Can I use Tailwind classes instead of CSS variables?**

A: Yes! The `tailwind.config.js` extends the theme with our design tokens:

```svelte
<!-- This works -->
<div class="bg-primary-600 text-white p-4 rounded-lg">

<!-- This also works -->
<div style="background: var(--color-primary-600); padding: var(--space-4);">
```

**Recommendation**: Use Tailwind for utility classes, CSS variables for custom components.

---

**Q: Some colors are missing from Tailwind config. Why?**

A: Only commonly used colors are in Tailwind config. For Lexikon-specific colors (e.g., relation types), use CSS variables:

```css
.relation-isa {
  background: var(--color-relation-isa);
}
```

---

### Components

**Q: Button component doesn't dispatch click event when disabled. Is this a bug?**

A: No, this is intentional. The `handleClick` function checks `!disabled && !loading` before dispatching. This prevents accidental double-submissions.

---

**Q: Input character counter shows wrong count for emojis. How to fix?**

A: JavaScript `.length` counts UTF-16 code units, not graphemes. For accurate counting:

```typescript
// In Input.svelte
import { countGraphemes } from '$lib/utils/string';

$: charCount = countGraphemes(value);
```

Then create `src/lib/utils/string.ts`:

```typescript
export function countGraphemes(str: string): number {
  return Array.from(new Intl.Segmenter().segment(str)).length;
}
```

---

**Q: How do I add icons to buttons?**

A: Use Lucide Svelte icons as slot content:

```svelte
<script>
  import Button from '$lib/components/Button.svelte';
  import { ArrowRight } from 'lucide-svelte';
</script>

<Button variant="primary">
  Continuer
  <ArrowRight size={16} />
</Button>
```

---

### Wireframes

**Q: Wireframes use inline styles. Should I copy those exactly?**

A: No. Wireframes are for **visual reference and interaction patterns**. In your Svelte components, use:
1. Design tokens (CSS variables or Tailwind)
2. Component props for variations
3. Clean, reusable code

The wireframes show pixel-perfect spacing, colors, and states - replicate the **visual design**, not the implementation.

---

**Q: Can I modify wireframe designs?**

A: Minor tweaks are OK (e.g., adjust spacing for better alignment). For significant changes:
1. Document the change reason
2. Get UX Designer approval
3. Update user story acceptance criteria

---

### User Stories

**Q: User story says "20-30 user stories total" but I only see 2. Where are the rest?**

A: The UX Designer created detailed stories for the **2 critical screens** (onboarding + quick draft) to unblock Sprint 1. Remaining stories (US-003 to US-030) will be written as needed for Sprint 2+.

**Current Priority**: Focus on US-001 and US-002 first.

---

**Q: Acceptance criteria mentions analytics tracking. Do I need to implement this now?**

A: For Sprint 1, use placeholder console.logs:

```typescript
function trackEvent(name: string, data: any) {
  console.log('[Analytics]', name, data);
  // TODO: Replace with real analytics (PostHog, Plausible, etc.)
}

trackEvent('onboarding_level_selected', { level: selectedLevel });
```

Replace with real analytics SDK in Sprint 2.

---

### Auto-Save

**Q: Auto-save fires too frequently and impacts performance. How to optimize?**

A: Current implementation uses 1-second debounce. If still slow:

```typescript
// Option 1: Increase debounce
autoSaveTimeout = setTimeout(() => { /* ... */ }, 2000); // 2 seconds

// Option 2: Only save if value changed
let lastSavedValue = '';
function autoSave() {
  const currentValue = JSON.stringify({ termName, definition, domain });
  if (currentValue === lastSavedValue) return;

  lastSavedValue = currentValue;
  // ... save logic
}

// Option 3: Use IndexedDB instead of localStorage (for large data)
import { openDB } from 'idb';
```

---

### Progressive Enhancement

**Q: Wireframes use JavaScript extensively. What about users with JS disabled?**

A: For Lexikon, JavaScript is **required** (SvelteKit is JS-first). However:

1. Show a `<noscript>` message:

```html
<noscript>
  <div class="p-8 text-center">
    <p>Lexikon nécessite JavaScript pour fonctionner.</p>
    <p>Veuillez activer JavaScript dans votre navigateur.</p>
  </div>
</noscript>
```

2. For critical forms (e.g., login), provide fallback:

```svelte
<!-- Form works with JS disabled (posts to server) -->
<form method="POST" action="/api/login" use:enhance>
  <!-- Fields -->
</form>
```

---

## Next Steps

### Immediate Actions (This Week)

1. **Setup Environment**: Clone repo, install dependencies, run dev server
2. **Test Components**: Create test page with Button, Input, Textarea
3. **Review Wireframes**: Open HTML files, inspect interactions
4. **Read User Stories**: Understand US-001 and US-002 acceptance criteria
5. **Ask Questions**: Slack channel `#lexikon-dev` or tag UX Designer

### Sprint 1 Kickoff (Next Week)

1. **Sprint Planning**: Review US-001 and US-002, estimate story points
2. **Task Breakdown**: Create subtasks in Jira/Linear
3. **Assign Work**: Developers pick tasks
4. **Daily Standups**: Track progress, unblock issues

### Communication

- **Design Questions**: Tag `@ux-designer` in Slack
- **Technical Blockers**: Tag `@tech-lead`
- **Urgent Issues**: Post in `#lexikon-urgent`

---

## Resources

### Documentation

- **UX Analysis**: `docs/analyses/analyse-ux-parcours-critiques-v03.md`
- **Design System**: `docs/design/design-system-figma-guide.md`
- **Execution Plan**: `docs/design/ux-designer-execution-plan.md`

### Design Assets

- **Tokens**: `docs/design/design-tokens.{css,json}`
- **Tailwind Config**: `docs/design/tailwind.config.js`
- **Icons**: `docs/design/icons-library.md`

### Code

- **Components**: `src/lib/components/`
- **Wireframes**: `wireframes/`
- **User Stories**: `user-stories/`

### External Resources

- **SvelteKit Docs**: https://kit.svelte.dev/docs
- **Tailwind Docs**: https://tailwindcss.com/docs
- **Lucide Icons**: https://lucide.dev/icons
- **WCAG Guidelines**: https://www.w3.org/WAI/WCAG21/quickref/

---

## Contact

**UX Designer**: Claude (this handoff)
**Tech Lead**: [TBD]
**Product Manager**: [TBD]

**Office Hours**: [TBD] - Ask design questions

---

**Last Updated**: 2025-11-14
**Version**: 1.0.0
**Status**: ✅ Ready for Development

---

**Good luck building Lexikon! 🚀**

*This guide is a living document. If you find gaps or have suggestions, please update it and commit changes.*
