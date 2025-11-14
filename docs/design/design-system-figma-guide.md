# 🎨 Lexikon - Design System & Wireframes Guide
## Guide Complet pour Implémentation Figma

**Version** : v0.1
**Date** : 2025-11-14
**Target** : Figma implementation
**Based on** : Shadcn/ui + TailwindCSS

---

## 📁 Structure Figma File

### Organisation des Pages

```
📄 Lexikon Design System v0.1
├─ 📄 Page 1: Cover & Info
│  └─ Frame: Project overview, changelog, guidelines
│
├─ 📄 Page 2: Design Tokens
│  ├─ Frame: Color Palette
│  ├─ Frame: Typography Scale
│  ├─ Frame: Spacing System
│  └─ Frame: Elevation & Shadows
│
├─ 📄 Page 3: Components Library
│  ├─ Frame: Buttons (all variants)
│  ├─ Frame: Inputs & Forms
│  ├─ Frame: Feedback (toasts, alerts)
│  ├─ Frame: Layout (cards, modals)
│  └─ Frame: Navigation
│
├─ 📄 Page 4: Wireframes (Low-Fidelity)
│  ├─ Frame 1: Onboarding - Choix niveau
│  ├─ Frame 2: Création terme - Quick Draft
│  ├─ Frame 3: Assistant relations IA
│  ├─ Frame 4: Import wizard - Mapping
│  ├─ Frame 5: Validation collaborative
│  └─ Frame 6: Configuration LLM
│
├─ 📄 Page 5: Mockups (High-Fidelity)
│  ├─ Desktop (1440x900)
│  │  └─ Same 6 screens
│  └─ Mobile (375x812)
│     └─ Responsive versions
│
└─ 📄 Page 6: User Flows
   ├─ Flow: Quick Project Onboarding
   ├─ Flow: Research Project Creation
   └─ Flow: API Integration
```

### Frames Standards

```
Desktop:
- Large: 1440 × 900 (primary)
- Medium: 1280 × 720

Tablet:
- iPad: 768 × 1024

Mobile:
- iPhone 14: 390 × 844
- Small: 375 × 812
```

---

## 🎨 Design Tokens

### 1. Palette Couleurs (Tons Académiques)

#### Couleurs Primaires

```css
/* Primary - Bleu Académique (Confiance, Sérieux) */
--primary-50:  #eff6ff;  /* Très clair - backgrounds */
--primary-100: #dbeafe;  /* Clair - hover states */
--primary-200: #bfdbfe;
--primary-300: #93c5fd;
--primary-400: #60a5fa;
--primary-500: #3b82f6;  /* Base - CTA, links */
--primary-600: #2563eb;  /* Default state */
--primary-700: #1d4ed8;  /* Active, pressed */
--primary-800: #1e40af;
--primary-900: #1e3a8a;  /* Très foncé - textes */

/* Secondary - Violet Innovation (IA, Suggestions) */
--secondary-50:  #faf5ff;
--secondary-100: #f3e8ff;
--secondary-200: #e9d5ff;
--secondary-300: #d8b4fe;
--secondary-400: #c084fc;
--secondary-500: #a855f7;  /* Base - AI features */
--secondary-600: #9333ea;
--secondary-700: #7e22ce;
--secondary-800: #6b21a8;
--secondary-900: #581c87;

/* Accent - Ambre Énergie (Actions importantes) */
--accent-50:  #fffbeb;
--accent-100: #fef3c7;
--accent-200: #fde68a;
--accent-300: #fcd34d;
--accent-400: #fbbf24;
--accent-500: #f59e0b;  /* Base - highlights */
--accent-600: #d97706;
--accent-700: #b45309;
--accent-800: #92400e;
--accent-900: #78350f;
```

#### Couleurs Sémantiques

```css
/* Success - Validation OK */
--success-50:  #ecfdf5;
--success-100: #d1fae5;
--success-500: #10b981;  /* Base */
--success-600: #059669;
--success-700: #047857;

/* Warning - Révision Nécessaire */
--warning-50:  #fefce8;
--warning-100: #fef9c3;
--warning-500: #eab308;  /* Base */
--warning-600: #ca8a04;
--warning-700: #a16207;

/* Error - Rejeté, Erreurs */
--error-50:  #fef2f2;
--error-100: #fee2e2;
--error-500: #ef4444;  /* Base */
--error-600: #dc2626;
--error-700: #b91c1c;

/* Info - Informations, Tips */
--info-50:  #f0f9ff;
--info-100: #e0f2fe;
--info-500: #06b6d4;  /* Base */
--info-600: #0891b2;
--info-700: #0e7490;
```

#### Couleurs Neutres (Grays)

```css
/* Neutral - Textes, Backgrounds, Bordures */
--gray-50:  #f9fafb;  /* Background très clair */
--gray-100: #f3f4f6;  /* Background clair */
--gray-200: #e5e7eb;  /* Bordures claires */
--gray-300: #d1d5db;  /* Bordures */
--gray-400: #9ca3af;  /* Placeholders */
--gray-500: #6b7280;  /* Textes secondaires */
--gray-600: #4b5563;  /* Textes */
--gray-700: #374151;  /* Textes importants */
--gray-800: #1f2937;  /* Titres */
--gray-900: #111827;  /* Textes très foncés */
--gray-950: #030712;  /* Quasi-noir */

/* Whites & Blacks */
--white: #ffffff;
--black: #000000;
```

#### Couleurs Spécifiques Lexikon

```css
/* Relation Types (pour visualisations ontologiques) */
--relation-isa:         #3b82f6;  /* is_a - Bleu */
--relation-partof:      #8b5cf6;  /* part_of - Violet */
--relation-employs:     #10b981;  /* employs - Vert */
--relation-opposes:     #ef4444;  /* opposes - Rouge */
--relation-related:     #6b7280;  /* related_to - Gris */
--relation-influenced:  #f59e0b;  /* influenced_by - Ambre */
--relation-causes:      #ec4899;  /* causes - Rose */
--relation-precedes:    #06b6d4;  /* precedes - Cyan */

/* Status Terms */
--status-draft:      #9ca3af;  /* Gris */
--status-proposed:   #f59e0b;  /* Ambre */
--status-review:     #3b82f6;  /* Bleu */
--status-validated:  #10b981;  /* Vert */
--status-rejected:   #ef4444;  /* Rouge */
--status-deprecated: #78350f;  /* Marron */
```

#### Application en Figma

```
Dans Figma:
1. Créer Styles > Color Styles
2. Organisation:
   ├─ Primary/50 à Primary/900
   ├─ Secondary/50 à Secondary/900
   ├─ Semantic/Success, Warning, Error, Info
   ├─ Neutral/Gray 50-950
   └─ Lexikon/Relations & Status

3. Naming convention:
   "Primary/600" (pas "Blue-600")
   → Facilite changement palette
```

### 2. Typography Scale

```css
/* Font Families */
--font-sans: 'Inter', system-ui, -apple-system, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
--font-serif: 'Merriweather', Georgia, serif;  /* Pour citations académiques */

/* Font Sizes (Scale 1.25 - Perfect Fourth) */
--text-xs:   0.75rem;   /* 12px - Labels, captions */
--text-sm:   0.875rem;  /* 14px - Body small, meta */
--text-base: 1rem;      /* 16px - Body default */
--text-lg:   1.125rem;  /* 18px - Body large */
--text-xl:   1.25rem;   /* 20px - H6, small titles */
--text-2xl:  1.5rem;    /* 24px - H5 */
--text-3xl:  1.875rem;  /* 30px - H4 */
--text-4xl:  2.25rem;   /* 36px - H3 */
--text-5xl:  3rem;      /* 48px - H2 */
--text-6xl:  3.75rem;   /* 60px - H1, hero */

/* Line Heights */
--leading-none:    1;
--leading-tight:   1.25;
--leading-snug:    1.375;
--leading-normal:  1.5;    /* Default body */
--leading-relaxed: 1.625;
--leading-loose:   2;

/* Font Weights */
--font-light:      300;
--font-normal:     400;
--font-medium:     500;
--font-semibold:   600;
--font-bold:       700;
--font-extrabold:  800;

/* Letter Spacing */
--tracking-tighter: -0.05em;
--tracking-tight:   -0.025em;
--tracking-normal:  0;
--tracking-wide:    0.025em;
--tracking-wider:   0.05em;
--tracking-widest:  0.1em;
```

#### Text Styles Figma

```
Créer Text Styles:

Headings:
├─ H1/Display: 48px, Bold (700), -0.025em, 1.2 lh
├─ H2/Title: 36px, Bold (700), -0.025em, 1.25 lh
├─ H3/Section: 30px, SemiBold (600), 0, 1.3 lh
├─ H4/Subsection: 24px, SemiBold (600), 0, 1.35 lh
├─ H5/Card Title: 20px, Medium (500), 0, 1.4 lh
└─ H6/Small Title: 18px, Medium (500), 0, 1.4 lh

Body:
├─ Body/Large: 18px, Regular (400), 0, 1.625 lh
├─ Body/Default: 16px, Regular (400), 0, 1.5 lh
├─ Body/Small: 14px, Regular (400), 0, 1.5 lh
└─ Body/Tiny: 12px, Regular (400), 0, 1.5 lh

Special:
├─ Label/Large: 14px, Medium (500), 0.025em, 1.25 lh
├─ Label/Small: 12px, Medium (500), 0.025em, 1.25 lh
├─ Code/Inline: 14px, Mono (400), 0, 1.5 lh
├─ Code/Block: 13px, Mono (400), 0, 1.6 lh
└─ Quote: 18px, Serif Italic (400), 0, 1.75 lh
```

### 3. Spacing System

```css
/* Spacing Scale (Base 4px) */
--space-0:  0;
--space-1:  0.25rem;  /* 4px */
--space-2:  0.5rem;   /* 8px */
--space-3:  0.75rem;  /* 12px */
--space-4:  1rem;     /* 16px - Base unit */
--space-5:  1.25rem;  /* 20px */
--space-6:  1.5rem;   /* 24px */
--space-8:  2rem;     /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
--space-32: 8rem;     /* 128px */

/* Semantic Spacing */
--space-xs:  var(--space-2);   /* 8px - Tight */
--space-sm:  var(--space-3);   /* 12px - Small gaps */
--space-md:  var(--space-4);   /* 16px - Default */
--space-lg:  var(--space-6);   /* 24px - Section spacing */
--space-xl:  var(--space-8);   /* 32px - Large sections */
--space-2xl: var(--space-12);  /* 48px - Page sections */
--space-3xl: var(--space-16);  /* 64px - Hero spacing */

/* Component-Specific */
--padding-input:   0.5rem 0.75rem;    /* 8px 12px */
--padding-button:  0.625rem 1.25rem;  /* 10px 20px */
--padding-card:    1.5rem;             /* 24px */
--padding-modal:   2rem;               /* 32px */
```

### 4. Border Radius

```css
/* Border Radius */
--radius-none: 0;
--radius-sm:   0.25rem;  /* 4px - Subtle */
--radius-md:   0.375rem; /* 6px - Default inputs */
--radius-lg:   0.5rem;   /* 8px - Cards */
--radius-xl:   0.75rem;  /* 12px - Large cards */
--radius-2xl:  1rem;     /* 16px - Modals */
--radius-full: 9999px;   /* Circular - Badges, avatars */

/* Component Defaults */
--radius-button: var(--radius-md);
--radius-input:  var(--radius-md);
--radius-card:   var(--radius-lg);
--radius-modal:  var(--radius-xl);
--radius-badge:  var(--radius-full);
```

### 5. Shadows & Elevation

```css
/* Shadows (Layered elevation) */
--shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1),
             0 1px 2px -1px rgb(0 0 0 / 0.1);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1),
             0 2px 4px -2px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1),
             0 4px 6px -4px rgb(0 0 0 / 0.1);
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1),
             0 8px 10px -6px rgb(0 0 0 / 0.1);
--shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);

/* Focus Ring */
--ring-width: 2px;
--ring-offset: 2px;
--ring-color: var(--primary-500);
--ring: 0 0 0 var(--ring-width) var(--ring-color);

/* Component Elevation */
--elevation-card:   var(--shadow-sm);
--elevation-popup:  var(--shadow-md);
--elevation-modal:  var(--shadow-xl);
--elevation-toast:  var(--shadow-lg);
```

---

## 🧩 Composants Prioritaires (12 Components)

### 1. Button

**Variants** :
- Primary (CTA, actions principales)
- Secondary (actions secondaires)
- Outline (actions tertiaires)
- Ghost (navigation, liens)
- Danger (suppression, rejet)

**States** : Default, Hover, Active, Focus, Disabled, Loading

**Sizes** : Small (sm), Medium (md - default), Large (lg)

**Specs** :
```
Primary Button (Medium):
├─ Background: Primary-600
├─ Text: White, 14px Medium
├─ Padding: 10px 20px
├─ Radius: 6px
├─ Shadow: none
├─ Hover: Background → Primary-700
├─ Focus: Ring 2px Primary-500, offset 2px
├─ Disabled: Background → Gray-300, Text → Gray-500
└─ Loading: Icon spinning + "Loading..."

Small: Padding 8px 16px, Text 12px
Large: Padding 12px 24px, Text 16px
```

### 2. Input (Text)

**Variants** :
- Default
- With icon (left/right)
- With prefix/suffix text
- Textarea

**States** : Default, Focus, Error, Disabled, Read-only

**Specs** :
```
Input Medium:
├─ Border: 1px solid Gray-300
├─ Background: White
├─ Text: 16px Regular, Gray-900
├─ Placeholder: Gray-400
├─ Padding: 10px 12px
├─ Radius: 6px
├─ Focus: Border → Primary-500, Ring 2px Primary-500
├─ Error: Border → Error-500, Ring 2px Error-500
└─ Disabled: Background → Gray-50, Text → Gray-500

Label (above):
├─ Text: 14px Medium, Gray-700
├─ Margin-bottom: 6px
└─ Optional: Gray-500 (label)

Helper text (below):
├─ Text: 12px Regular, Gray-500
├─ Margin-top: 4px
└─ Error state: Error-600
```

### 3. Select / Dropdown

**Specs** :
```
Similar to Input but:
├─ Icon: Chevron-down (right)
├─ Dropdown menu:
│  ├─ Background: White
│  ├─ Border: 1px Gray-200
│  ├─ Shadow: shadow-lg
│  ├─ Radius: 8px
│  ├─ Max-height: 256px (scrollable)
│  └─ Options:
│     ├─ Padding: 10px 12px
│     ├─ Hover: Background Gray-50
│     └─ Selected: Background Primary-50, Text Primary-700
```

### 4. Checkbox & Radio

**Specs** :
```
Checkbox:
├─ Size: 16x16px (sm), 20x20px (md)
├─ Border: 2px Gray-300
├─ Radius: 4px
├─ Checked: Background Primary-600, Icon white checkmark
├─ Focus: Ring 2px Primary-500
└─ Label: 14px Regular, margin-left 8px

Radio:
├─ Size: 16x16px (sm), 20x20px (md)
├─ Border: 2px Gray-300
├─ Radius: full (circle)
├─ Checked: Background Primary-600, inner circle white 6px
└─ Same focus/label as checkbox
```

### 5. Card

**Variants** :
- Default (white background)
- Elevated (with shadow)
- Bordered (outline only)
- Interactive (hover effect)

**Specs** :
```
Card Default:
├─ Background: White
├─ Border: 1px Gray-200
├─ Radius: 12px
├─ Padding: 24px
├─ Shadow: none (or shadow-sm if elevated)
└─ Hover (if interactive): Shadow → shadow-md, Border → Primary-200

Card structure:
├─ Header (optional):
│  ├─ Title: H5 (20px SemiBold)
│  ├─ Subtitle: 14px Regular Gray-500
│  └─ Padding-bottom: 16px, Border-bottom 1px Gray-200
├─ Body:
│  └─ Padding: 16px 0
└─ Footer (optional):
   ├─ Padding-top: 16px, Border-top 1px Gray-200
   └─ Actions (buttons)
```

### 6. Modal / Dialog

**Specs** :
```
Modal:
├─ Backdrop: rgba(0,0,0,0.5)
├─ Container:
│  ├─ Background: White
│  ├─ Radius: 16px
│  ├─ Shadow: shadow-2xl
│  ├─ Max-width: 480px (sm), 640px (md), 800px (lg)
│  ├─ Padding: 32px
│  └─ Margin: 64px auto
├─ Header:
│  ├─ Title: H4 (24px SemiBold)
│  ├─ Close button: Ghost, top-right
│  └─ Padding-bottom: 24px
├─ Body:
│  └─ Scrollable if content > viewport
└─ Footer:
   ├─ Padding-top: 24px
   ├─ Border-top: 1px Gray-200
   └─ Actions: Align-right, gap 12px
```

### 7. Toast / Notification

**Variants** : Success, Error, Warning, Info

**Specs** :
```
Toast:
├─ Background: White
├─ Border: 1px + colored left-border 4px
├─ Radius: 8px
├─ Shadow: shadow-lg
├─ Padding: 16px
├─ Max-width: 420px
├─ Position: Fixed top-right, margin 16px
└─ Auto-dismiss: 5s (closeable)

Success:
├─ Left-border: Success-500
└─ Icon: Checkmark circle (Success-500)

Error:
├─ Left-border: Error-500
└─ Icon: X circle (Error-500)

Structure:
├─ Icon (left): 20x20px
├─ Content:
│  ├─ Title: 14px SemiBold
│  └─ Message: 14px Regular Gray-600
└─ Close button (right): Ghost sm
```

### 8. Badge / Tag

**Variants** : Default, Primary, Success, Warning, Error, Secondary

**Specs** :
```
Badge:
├─ Background: Gray-100 (default), colored variants
├─ Text: 12px Medium
├─ Padding: 4px 10px
├─ Radius: full (pill)
├─ Border: none

Primary:
├─ Background: Primary-100
└─ Text: Primary-700

Removable (tag):
├─ Same as badge
└─ Icon X (right): 12px, clickable
```

### 9. Progress Bar

**Specs** :
```
Progress:
├─ Track:
│  ├─ Background: Gray-200
│  ├─ Height: 8px (sm), 12px (md)
│  └─ Radius: full
└─ Fill:
   ├─ Background: Primary-600
   ├─ Width: 0-100%
   ├─ Radius: full
   └─ Transition: width 0.3s ease

With label:
├─ Above: "Step 2 of 5" (12px Medium)
└─ Percentage: "40%" (right-aligned)
```

### 10. Tabs

**Specs** :
```
Tabs:
├─ Container:
│  ├─ Border-bottom: 2px Gray-200
│  └─ Gap: 32px (between tabs)
└─ Tab item:
   ├─ Text: 14px Medium
   ├─ Padding: 12px 0
   ├─ Color: Gray-600 (inactive)
   ├─ Border-bottom: 2px transparent
   ├─ Hover: Color → Gray-900
   └─ Active:
      ├─ Color: Primary-600
      └─ Border-bottom: 2px Primary-600

Content panel:
└─ Padding-top: 24px
```

### 11. Tooltip

**Specs** :
```
Tooltip:
├─ Background: Gray-900
├─ Text: 12px Regular White
├─ Padding: 6px 10px
├─ Radius: 6px
├─ Shadow: shadow-md
├─ Arrow: 6px triangle (same color)
├─ Max-width: 240px
└─ Show on: Hover 0.5s delay
```

### 12. Alert / Banner

**Variants** : Info, Warning, Error, Success

**Specs** :
```
Alert:
├─ Background: Info-50 (variant)
├─ Border: 1px Info-200
├─ Radius: 8px
├─ Padding: 16px
└─ Margin-bottom: 16px

Structure:
├─ Icon (left): 20x20px Info-500
├─ Content:
│  ├─ Title: 14px SemiBold Info-800
│  ├─ Message: 14px Regular Info-700
│  └─ Link (optional): 14px Medium Info-600, underline
└─ Close (right): Ghost icon button
```

---

## 📱 Wireframes Conceptuels (6 Écrans)

### Wireframe 1 : Onboarding - Choix Niveau d'Adoption

```
┌─────────────────────────────────────────────────────────────┐
│                      LEXIKON LOGO                            │
│                                                               │
│         👋 Bienvenue sur Lexikon !                           │
│                                                               │
│    Comment prévoyez-vous d'utiliser Lexikon ?               │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ ○ Projet Rapide                          [🚀 Icon] │    │
│  │                                                       │    │
│  │ Étudiant, usage ponctuel                            │    │
│  │ "J'ai besoin d'une ontologie pour mon mémoire"      │    │
│  │                                                       │    │
│  │ • Setup en 30 minutes                                │    │
│  │ • Export quand terminé                               │    │
│  │ • Gratuit, pas de validation obligatoire            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ ○ Projet de Recherche                    [🎓 Icon] │    │
│  │                                                       │    │
│  │ Académique, 1-2 ans                                  │    │
│  │ "Je construis une ontologie de qualité pour         │    │
│  │  publication"                                        │    │
│  │                                                       │    │
│  │ • Validation experte, collaboration                  │    │
│  │ • Formule Pro recommandée                           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ ○ API Production                         [⚡ Icon] │    │
│  │                                                       │    │
│  │ Développeur, long-terme                              │    │
│  │ "J'intègre Lexikon dans mon application"            │    │
│  │                                                       │    │
│  │ • API-first, monitoring, SLA                         │    │
│  │ • Formule Team/Enterprise                           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│              [Pas sûr ? → Quiz 2 minutes]                    │
│                                                               │
│                    [Continuer →]                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘

Components used:
- Radio buttons (custom styled)
- Cards (interactive, hover state)
- Button primary (Continuer)
- Button ghost (Quiz)
- Icons (contextual)
```

### Wireframe 2 : Création Terme - Quick Draft (Niveau 1)

```
┌─────────────────────────────────────────────────────────────┐
│ LEXIKON          Brouillons (3) │ En révision (1) │ ⚙️ │ 👤│
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ← Retour aux termes                                         │
│                                                               │
│  Créer un nouveau terme                                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━     │
│                                                               │
│  📍 Étape 1 sur 3 : Quick Draft (Brouillon rapide)          │
│  ████████░░░░░░░░░░░░░░░░░░░░░░  30%                        │
│                                                               │
│  💡 Complétez ces 5 champs pour sauvegarder votre brouillon │
│     Temps estimé : 5 minutes                                 │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 1. Domaine *                                          │  │
│  │ [Sciences Humaines et Sociales       ▼]              │  │
│  │                                                        │  │
│  │ 2. Terme *                                            │  │
│  │ [____________________________________]                │  │
│  │   Ex: "aliénation", "hégémonie"                       │  │
│  │                                                        │  │
│  │ 3. Définition courte * (max 200 caractères)          │  │
│  │ [____________________________________]                │  │
│  │ [____________________________________]                │  │
│  │ 27/200 caractères                                     │  │
│  │   Une phrase claire et concise                        │  │
│  │                                                        │  │
│  │ 4. Auteur principal *                                 │  │
│  │ [Karl Marx                           ▼]              │  │
│  │                                                        │  │
│  │ 5. Citation source *                                  │  │
│  │ Titre: [____________________________]                │  │
│  │ Année: [1844]  Page: [58-59]                         │  │
│  │                                                        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ⚠️ Sauvegarde automatique activée (dernière: il y a 12s)   │
│                                                               │
│  [⬅️ Annuler]  [💾 Sauvegarder brouillon]  [Continuer →]   │
│                                                               │
│  ────────────────────────────────────────────────────────    │
│  Niveau 2 : Ready for Review (20 min) →                     │
│  Niveau 3 : Expert Complete (45 min) →                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘

Components:
- Progress bar (étapes wizard)
- Alert info (temps estimé)
- Form inputs (text, select, textarea)
- Character counter
- Auto-save indicator
- Button variants (ghost, secondary, primary)
- Badge (étape)
```

### Wireframe 3 : Assistant Relations IA

```
┌─────────────────────────────────────────────────────────────┐
│ LEXIKON                                           ⚙️ │ 👤   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Terme : "Aliénation"                          [Éditer]      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━     │
│                                                               │
│  ⚡ Relations Ontologiques                                   │
│                                                               │
│  💡 L'IA a détecté 5 relations potentielles dans votre      │
│     définition. Acceptez, modifiez ou refusez.              │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 🤖 SUGGESTION AUTOMATIQUE                Confiance: 85%│  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ Relation suggérée : is_a                              │  │
│  │ Terme cible : "dépossession"                          │  │
│  │                                                        │  │
│  │ 📝 Justification :                                    │  │
│  │ Le terme "dépossession" a été détecté comme terme     │  │
│  │ parent dans la définition longue. Les deux concepts   │  │
│  │ partagent 87% de contexte sémantique.                 │  │
│  │                                                        │  │
│  │ [✓ Accepter]  [✏️ Modifier]  [✗ Refuser]             │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 🤖 SUGGESTION AUTOMATIQUE                Confiance: 75%│  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ Relation suggérée : employs                           │  │
│  │ Terme cible : "travail"                               │  │
│  │                                                        │  │
│  │ 📝 Justification :                                    │  │
│  │ "Travail" est un concept central utilisé 4 fois dans │  │
│  │ votre définition marxiste.                            │  │
│  │                                                        │  │
│  │ [✓ Accepter]  [✏️ Modifier]  [✗ Refuser]             │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 🤖 SUGGESTION                            Confiance: 90%│  │
│  │ opposes → "émancipation"                              │  │
│  │ [✓]  [✏️]  [✗]                                        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  + Ajouter relation manuellement                             │
│                                                               │
│  Relations acceptées (2):                                    │
│  • is_a → dépossession                                       │
│  • opposes → émancipation                                    │
│                                                               │
│  [← Retour]              [Ignorer tout]  [Continuer →]      │
│                                                               │
└─────────────────────────────────────────────────────────────┘

Components:
- Alert info (AI notice)
- Card elevated (suggestion)
- Badge (confiance %)
- Icons (AI, types relations)
- Button group (Accept/Edit/Reject)
- Collapsible cards
- List items (relations acceptées)
```

### Wireframe 4 : Import Wizard - Mapping Colonnes

```
┌─────────────────────────────────────────────────────────────┐
│ LEXIKON                                           ⚙️ │ 👤   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Import de données                                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━     │
│                                                               │
│  📍 Étape 2 sur 4 : Mapping des colonnes                    │
│  ████████████░░░░░░░░░░░░  50%                              │
│                                                               │
│  ✓ Fichier détecté : glossaire_SHS.xlsx                     │
│    247 lignes • Format: Excel • Encodage: UTF-8             │
│                                                               │
│  Associez vos colonnes aux champs Lexikon :                 │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Votre colonne          →    Champ Lexikon             │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │                                                        │  │
│  │ "Terme"                →    [term.label           ▼] ✓│  │
│  │ Détection auto                                        │  │
│  │                                                        │  │
│  │ "Définition"           →    [definitions.short    ▼] ?│  │
│  │                             [definitions.long]        │  │
│  │ ⚠️ Ambigu - Choisissez le bon champ                  │  │
│  │                                                        │  │
│  │ "Auteur"               →    [authors[0].name      ▼] ✓│  │
│  │ Détection auto                                        │  │
│  │                                                        │  │
│  │ "Source"               →    [citations[0].title   ▼] ✓│  │
│  │ Détection auto                                        │  │
│  │                                                        │  │
│  │ "Date création"        →    [Ignorer cette colonne]  │  │
│  │ ℹ️ Colonne non mappée                                 │  │
│  │                                                        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 📊 PRÉVISUALISATION (3 premières lignes)             │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ Terme         │ Définition        │ Auteur           │  │
│  │ aliénation    │ Perte de maîtrise │ Karl Marx        │  │
│  │ hégémonie     │ Domination...     │ Antonio Gramsci  │  │
│  │ dialectique   │ Méthode...        │ G.W.F. Hegel     │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  [← Retour]                          [Continuer →]          │
│                                                               │
└─────────────────────────────────────────────────────────────┘

Components:
- Progress stepper
- Alert success (file detected)
- Select dropdowns (mapping)
- Icons (checkmark, warning, info)
- Table (preview)
- Badges (auto-détection)
```

### Wireframe 5 : Validation Collaborative

```
┌─────────────────────────────────────────────────────────────┐
│ LEXIKON                                           ⚙️ │ 👤   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ← Retour à la file de validation                           │
│                                                               │
│  Validation : "Aliénation"                                   │
│  Créé par Dr. Marie Dupont • Il y a 2 jours                 │
│  👁️ 2 personnes consultent actuellement                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━     │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 📝 Définition courte                           ✅ OK  │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ "Perte de maîtrise de soi ou de sa production..."    │  │
│  │                                                        │  │
│  │ 💬 Prof. Jean Martin (il y a 2h) :                   │  │
│  │    "Excellente synthèse concise."                     │  │
│  │    [Répondre] [✓ Marquer résolu]                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 📝 Définition longue                          💬 3    │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ "L'aliénation désigne le processus par lequel..."    │  │
│  │                                                        │  │
│  │ 💬 Prof. Jean Martin (il y a 1h) :                   │  │
│  │    "Ajouter la dimension psychanalytique (Lacan)"    │  │
│  │    [Répondre] [Marquer résolu]                        │  │
│  │                                                        │  │
│  │    ↳ Dr. Marie Dupont (il y a 30min) :               │  │
│  │       "Bonne idée, j'ajoute une section."            │  │
│  │                                                        │  │
│  │ [+ Ajouter un commentaire...]                         │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 🔗 Relations (5)                               ⚠️     │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ • is_a → dépossession                          ✅     │  │
│  │ • employs → travail                            ✅     │  │
│  │ • opposes → émancipation                       ❌     │  │
│  │                                                        │  │
│  │   💬 Prof. Jean Martin :                              │  │
│  │      "Relation trop simpliste. L'émancipation est    │  │
│  │       plus nuancée que l'opposé direct."             │  │
│  │      [Répondre] [Marquer résolu]                      │  │
│  │                                                        │  │
│  │ [+ Voir toutes les relations...]                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  VOTRE VALIDATION :                                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Définitions :         [Excellent      ▼]             │  │
│  │ Relations :           [Besoin révision▼]             │  │
│  │ Citations :           [Valide         ▼]             │  │
│  │ Cohérence globale :   [Bonne          ▼]             │  │
│  │                                                        │  │
│  │ DÉCISION FINALE :                                     │  │
│  │ ○ Approuver tel quel                                  │  │
│  │ ● Approuver avec suggestions mineures                │  │
│  │ ○ Demander révision majeure                          │  │
│  │ ○ Rejeter                                             │  │
│  │                                                        │  │
│  │ Commentaire général (optionnel) :                    │  │
│  │ [________________________________________________]    │  │
│  │                                                        │  │
│  │              [Soumettre ma validation]               │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘

Components:
- Timeline / Activity feed
- Comment threads (nested)
- Status badges (✅ ⚠️ ❌)
- Avatar indicators (who's viewing)
- Collapsible sections
- Form validation (dropdowns, radio, textarea)
- Real-time updates indicator
```

### Wireframe 6 : Configuration LLM (BYOK)

```
┌─────────────────────────────────────────────────────────────┐
│ LEXIKON                                           ⚙️ │ 👤   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ⚙️ Configuration                                            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━     │
│                                                               │
│  Général │ Domaines │ **LLM & API** │ Facturation │ Équipe  │
│                                                               │
│  🤖 Configuration LLM                                        │
│                                                               │
│  Comment voulez-vous utiliser les modèles de langage ?      │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ ● J'ai ma propre clé API (BYOK)              💰 €0   │  │
│  │   Recommandé pour contrôle des coûts                  │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │   Provider :                                           │  │
│  │   [OpenAI (GPT-4, GPT-3.5)               ▼]          │  │
│  │                                                        │  │
│  │   Votre clé API :                                     │  │
│  │   [sk-proj-••••••••••••••••••••••] 🔒 [Tester]       │  │
│  │   ✓ Clé valide • Dernière vérification: il y a 2h    │  │
│  │                                                        │  │
│  │   Usage actuel (30 jours):                            │  │
│  │   • 2.3M tokens (~€87.50 facturés par OpenAI)        │  │
│  │   • 1,247 requêtes enrichissement                     │  │
│  │   • Coût Lexikon: €0 (BYOK gratuit ✓)               │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ ○ Utiliser LLM gratuits (limité)        100 req/jour│  │
│  │   Idéal pour tests et petits projets                  │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │   • Openrouter : Llama 3, Mixtral                     │  │
│  │   • Limite: 100 requêtes/jour (réinitialisation UTC) │  │
│  │   • Aujourd'hui: 23/100 utilisées                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ ○ Pay-as-you-go Lexikon         Solde: €47.50       │  │
│  │   Pas de clé API nécessaire                           │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │   • €0.002/1K tokens entrée                           │  │
│  │   • €0.006/1K tokens sortie                           │  │
│  │   • Facturation mensuelle                             │  │
│  │   • [+ Recharger crédits]                             │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 📊 DASHBOARD TRANSPARENCE (30 jours)                  │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ Lexikon Pro :              €49.00                     │  │
│  │   • Ontology hosting & validation                     │  │
│  │                                                        │  │
│  │ LLM (BYOK - GPT-4) :      €87.50                     │  │
│  │   • 2.3M tokens (votre compte OpenAI)                │  │
│  │   • Facturé directement par OpenAI                    │  │
│  │                                                        │  │
│  │ ─────────────────────────────────────────────────     │  │
│  │ Total :                   €136.50                     │  │
│  │   • Lexikon: €49.00 (36%)                            │  │
│  │   • LLM: €87.50 (64%)                                │  │
│  │                                                        │  │
│  │ 💡 Astuce: Passez à GPT-3.5 pour réduire vos coûts  │  │
│  │    LLM de 90% (€87.50 → €8.75)                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  [Annuler]                      [Sauvegarder modifications] │
│                                                               │
└─────────────────────────────────────────────────────────────┘

Components:
- Tabs navigation
- Radio cards (selectable modes)
- Input password (API key)
- Button ghost (Tester)
- Alert success (clé valide)
- Progress bar (usage quota)
- Card (dashboard coûts)
- Alert info (astuce)
- Badge (pricing)
```

---

## 📋 Checklist Implémentation Figma

### Phase 1 : Setup (Jour 1)

```
□ Créer fichier Figma "Lexikon Design System v0.1"
□ Définir frames standards (Desktop 1440, Mobile 375)
□ Installer plugins:
  □ Iconify (pour Lucide icons)
  □ Stark (accessibilité)
  □ Content Reel (faux contenu)
  □ TailwindCSS
```

### Phase 2 : Design Tokens (Jour 1-2)

```
□ Créer Color Styles (toutes les couleurs définies)
□ Créer Text Styles (12 styles typographiques)
□ Définir grille 8px (spacing system)
□ Créer Effect Styles (shadows)
□ Variables Figma (si Figma Pro):
  □ Color variables
  □ Spacing variables
```

### Phase 3 : Components (Jour 2-3)

```
□ Button (5 variants × 3 sizes × 5 states = 75 variantes)
□ Input (4 types × 3 states = 12 variantes)
□ Select / Dropdown
□ Checkbox & Radio
□ Card (4 variants)
□ Modal
□ Toast (4 variants)
□ Badge (6 variants)
□ Progress
□ Tabs
□ Tooltip
□ Alert (4 variants)

Pour chaque composant:
□ Créer variants Figma (states, sizes)
□ Auto-layout configuré
□ Responsive constraints
□ Documentation (description)
```

### Phase 4 : Wireframes (Jour 4-5)

```
□ Écran 1: Onboarding choix niveau
□ Écran 2: Création terme Quick Draft
□ Écran 3: Assistant relations IA
□ Écran 4: Import wizard mapping
□ Écran 5: Validation collaborative
□ Écran 6: Configuration LLM

Pour chaque écran:
□ Version desktop (1440px)
□ Version mobile (375px) - optionnel v0.1
□ Annotations (specs, interactions)
□ Prototypage cliquable
```

### Phase 5 : Prototypage (Jour 5)

```
□ Lier les écrans (flows)
□ Interactions de base:
  □ Hover states
  □ Click → Navigate
  □ Overlay modals
□ Smart Animate (transitions)
□ Tester le prototype (self-test)
```

### Phase 6 : Documentation & Handoff (Jour 6)

```
□ Page Cover avec:
  □ Overview du projet
  □ Guidelines d'utilisation
  □ Changelog
□ Specs CSS export (Inspect mode)
□ Assets export:
  □ Icons SVG
  □ Logo variations
□ Partage avec équipe dev
□ Session walkthrough (30 min)
```

---

## 🎨 Recommandations Finales

### Accessibilité (WCAG AA)

```
Contraste minimum:
- Texte normal: 4.5:1
- Texte large (>18px): 3:1
- UI elements: 3:1

Tailles touch:
- Boutons minimum: 44×44px
- Espacement: 8px minimum

Focus visible:
- Ring 2px couleur contrastée
- Ne jamais supprimer outline
```

### Performance Figma

```
Optimisations:
- Utiliser Instances (pas de duplication)
- Components imbriqués (DRY)
- Pages séparées (wireframes ≠ components)
- Limiter effects lourds (blur)
```

### Collaboration

```
Conventions nommage:
- Components: "Button/Primary/Medium/Default"
- Frames: "01 - Onboarding - Choix niveau"
- Layers: Descriptifs (pas "Rectangle 47")

Annotations:
- 📏 Specs techniques
- ⚠️ Edge cases
- 💡 Idées / Notes
- ✅ Validé dev
```

---

**Prochaines étapes** :
1. Créer le fichier Figma avec cette structure
2. Implémenter les design tokens (1 jour)
3. Créer les 12 composants (2 jours)
4. Wireframes 6 écrans (2 jours)
5. Tests utilisateurs (1 jour)
6. Ajustements (1 jour)

**Total : ~1 semaine de travail UX Designer**

Ce guide vous donne toutes les spécifications pour implémenter rapidement et proprement dans Figma. Besoin de précisions sur un composant ou un écran spécifique ?
