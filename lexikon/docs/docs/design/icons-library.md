# 🎨 Lexikon Icons Library
## Lucide Icons Selection & Usage Guide

**Version** : 0.1
**Icon Set** : [Lucide Icons](https://lucide.dev)
**Total Icons Selected** : 30 priority icons
**Installation** : `npm install lucide-svelte`

---

## 📦 Priority Icons (30)

### Navigation & UI (8 icons)

| Icon | Name | Use Case | Size Default |
|------|------|----------|--------------|
| ☰ | `Menu` | Mobile menu toggle | 24px |
| ✕ | `X` | Close modals, dismiss toast | 20px |
| ← | `ChevronLeft` | Back navigation, prev | 20px |
| → | `ChevronRight` | Forward, next | 20px |
| ↓ | `ChevronDown` | Dropdown indicator, expand | 16px |
| ↑ | `ChevronUp` | Collapse, scroll to top | 16px |
| ⚙ | `Settings` | Settings page, config | 20px |
| 👤 | `User` | Profile, account | 20px |

### Actions (7 icons)

| Icon | Name | Use Case | Size Default |
|------|------|----------|--------------|
| ✓ | `Check` | Success, validation OK, checkbox | 20px |
| + | `Plus` | Add term, add relation, new | 20px |
| ✎ | `Pencil` | Edit, modify | 18px |
| 🗑 | `Trash2` | Delete, remove | 18px |
| 💾 | `Save` | Save draft, save changes | 20px |
| ↻ | `RefreshCw` | Reload, retry | 20px |
| ⊕ | `Copy` | Duplicate, copy to clipboard | 18px |

### Content & Files (5 icons)

| Icon | Name | Use Case | Size Default |
|------|------|----------|--------------|
| 📄 | `FileText` | Document, term, article | 20px |
| 📁 | `Folder` | Domain, collection | 20px |
| 📤 | `Upload` | Import file, upload | 20px |
| 📥 | `Download` | Export, download | 20px |
| 🔍 | `Search` | Search bar, find | 20px |

### Status & Feedback (6 icons)

| Icon | Name | Use Case | Size Default |
|------|------|----------|--------------|
| ✓ | `CheckCircle` | Success message, validated | 20px |
| ⚠ | `AlertTriangle` | Warning, needs review | 20px |
| ✕ | `XCircle` | Error, rejected | 20px |
| ℹ | `Info` | Information, help | 20px |
| ⏱ | `Clock` | Pending, in review | 20px |
| ⚡ | `Zap` | AI feature, automated | 20px |

### Collaboration & Communication (4 icons)

| Icon | Name | Use Case | Size Default |
|------|------|----------|--------------|
| 💬 | `MessageSquare` | Comments, discussion | 20px |
| 👥 | `Users` | Team, collaborators | 20px |
| 👁 | `Eye` | View, visibility, watchers | 18px |
| 🔔 | `Bell` | Notifications | 20px |

---

## 🎯 Usage Guidelines

### Sizing

```css
/* Icon Sizes */
.icon-xs { width: 12px; height: 12px; }  /* Inline text */
.icon-sm { width: 16px; height: 16px; }  /* Buttons, labels */
.icon-md { width: 20px; height: 20px; }  /* Default */
.icon-lg { width: 24px; height: 24px; }  /* Nav, headers */
.icon-xl { width: 32px; height: 32px; }  /* Feature icons */
```

### Colors

```css
/* Semantic Colors */
.icon-default  { color: var(--color-gray-600); }
.icon-muted    { color: var(--color-gray-400); }
.icon-primary  { color: var(--color-primary-600); }
.icon-success  { color: var(--color-success-500); }
.icon-warning  { color: var(--color-warning-500); }
.icon-error    { color: var(--color-error-500); }
.icon-info     { color: var(--color-info-500); }
```

### Stroke Width

```css
/* Stroke weights */
.icon-thin     { stroke-width: 1.5; }   /* Subtle */
.icon-regular  { stroke-width: 2; }     /* Default */
.icon-bold     { stroke-width: 2.5; }   /* Emphasis */
```

---

## 🔧 Implementation

### Svelte Component

```svelte
<!-- src/lib/components/Icon.svelte -->
<script lang="ts">
  import { icons } from 'lucide-svelte';

  export let name: string;
  export let size: 'xs' | 'sm' | 'md' | 'lg' | 'xl' = 'md';
  export let color: string | undefined = undefined;
  export let className: string = '';

  const sizes = {
    xs: 12,
    sm: 16,
    md: 20,
    lg: 24,
    xl: 32
  };

  $: IconComponent = icons[name];
</script>

{#if IconComponent}
  <IconComponent
    size={sizes[size]}
    class="{className}"
    style:color
  />
{/if}
```

### Usage Examples

```svelte
<!-- Primary button with icon -->
<Button variant="primary">
  <Icon name="Plus" size="sm" />
  Add Term
</Button>

<!-- Success toast -->
<Toast variant="success">
  <Icon name="CheckCircle" color="var(--color-success-500)" />
  Term validated successfully
</Toast>

<!-- Status badge -->
<Badge variant="warning">
  <Icon name="Clock" size="xs" />
  In Review
</Badge>
```

---

## 📐 Accessibility

### Required Attributes

```svelte
<!-- Decorative icon (with text label) -->
<Icon name="Search" aria-hidden="true" />
<span>Search</span>

<!-- Functional icon (no text) -->
<button aria-label="Close">
  <Icon name="X" />
</button>

<!-- Icon with tooltip -->
<Icon name="Info" aria-describedby="tooltip-1" />
<Tooltip id="tooltip-1">More information</Tooltip>
```

### Touch Targets

```css
/* Minimum 44x44px for touch */
button.icon-only {
  min-width: 44px;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

---

## 🎨 Icon Naming Convention

### File Naming
```
icon-{name}-{variant}.svg

Examples:
- icon-check.svg
- icon-chevron-down.svg
- icon-file-text.svg
```

### Component Props
```typescript
interface IconProps {
  name: string;           // Icon name (camelCase)
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  color?: string;         // CSS color value
  className?: string;     // Additional classes
  strokeWidth?: number;   // 1.5 | 2 | 2.5
}
```

---

## 🚀 Quick Reference

### Most Used Icons

```typescript
// Import in Svelte component
import {
  Plus, Check, X, ChevronDown,
  Search, Save, Pencil, Trash2,
  AlertTriangle, CheckCircle, XCircle, Info
} from 'lucide-svelte';
```

### Icon + Text Alignment

```css
/* Horizontal alignment */
.flex-icon {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem; /* 8px */
}

/* Example */
<span class="flex-icon">
  <Icon name="Zap" size="sm" />
  AI Suggestion
</span>
```

---

## 📦 Export Checklist

For production, optimize icons:

```bash
# Install SVGO
npm install -D svgo

# Optimize SVG
svgo icon.svg -o icon.optimized.svg

# Options to preserve:
- viewBox attribute
- aria-* attributes
- Stroke properties
```

---

**Installation** : `npm install lucide-svelte`
**Documentation** : https://lucide.dev
**License** : ISC (free for commercial use)

*This library provides 30 carefully selected icons covering all Lexikon v0.1 use cases.*
