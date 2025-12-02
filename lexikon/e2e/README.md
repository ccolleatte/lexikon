# E2E Testing Guide for Lexikon

## Overview

This directory contains comprehensive E2E tests for Lexikon's Options 2 & 3 features using Playwright.

**Status**: Work in Progress - 42/147 tests implemented

## Test Files Status

- ✅ **search.spec.ts** (21 tests) - Search UI, filtering, results, accessibility
- ✅ **relations.spec.ts** (21 tests) - Relations display, CRUD, inferred relations
- 🔲 **mobile-navigation.spec.ts** (16 tests) - Hamburger menu, responsive nav
- 🔲 **toast-notifications.spec.ts** (18 tests) - Toast types, timing, stacking
- 🔲 **vocabularies.spec.ts** (19 tests) - Import/export, file upload, preview
- 🔲 **analytics.spec.ts** (18 tests) - Charts, stat cards, data visualization
- 🔲 **dark-mode.spec.ts** (17 tests) - Theme toggle, persistence, styling
- 🔲 **loading-skeletons.spec.ts** (15 tests) - Skeleton loading, animations

## Running Tests

\`\`\`bash
# Run all E2E tests
npm run test:e2e

# Run specific test file
npm run test:e2e -- e2e/search.spec.ts

# Interactive UI mode
npm run test:e2e:ui

# With browser visible
npm run test:e2e:headed

# Debug mode
npm run test:e2e -- --debug e2e/search.spec.ts
\`\`\`

## Implementation Progress

### Completed (42 tests)
- ✅ search.spec.ts - 21 tests
- ✅ relations.spec.ts - 21 tests

### Remaining (105 tests)
- Mobile navigation (16 tests)
- Toast notifications (18 tests)
- Vocabularies import/export (19 tests)
- Analytics dashboard (18 tests)
- Dark mode (17 tests)
- Loading skeletons (15 tests)

## Test Pattern Examples

### Authentication
\`\`\`typescript
import { mockAuthState } from './helpers/auth-helpers';

test.beforeEach(async ({ page }) => {
  await mockAuthState(page);
  await page.goto('/terms');
});
\`\`\`

### API Mocking
\`\`\`typescript
import { mockApiSuccess, mockApiError } from './helpers/api-mocking';

await mockApiSuccess(page, '/api/endpoint', mockData);
await mockApiError(page, '/api/endpoint', 500, 'Error message');
\`\`\`

### Semantic Selectors (Preferred)
\`\`\`typescript
await page.getByRole('button', { name: /add relation/i });
await page.getByRole('searchbox');
await page.getByLabel(/email/i);
await page.getByText(/no results/i);
\`\`\`

### Mobile Testing
\`\`\`typescript
test.use({ viewport: { width: 375, height: 667 } });

test('should work on mobile', async ({ page }) => {
  // Mobile-specific test
});
\`\`\`

## Next Steps to Complete

The remaining 105 tests should follow the patterns established in search.spec.ts and relations.spec.ts:

1. **Use mockAuthState()** to setup authentication
2. **Use semantic selectors** (getByRole, getByLabel, getByText)
3. **Mock APIs** with mockApiSuccess/Error/Delay
4. **Test accessibility** - ARIA labels, roles, keyboard nav
5. **Test mobile viewports** - min 2 viewport sizes
6. **Test error scenarios** - API failures, validation
7. **Wait appropriately** - debounce, animations, async operations

## Helper Functions Available

- **mockAuthState(page)** - Setup authenticated user
- **clearAuthState(page)** - Clear all auth/theme/language
- **mockApiSuccess(page, endpoint, data)** - Mock successful response
- **mockApiError(page, endpoint, status, msg)** - Mock error response
- **mockApiWithDelay(page, endpoint, data, ms)** - Mock with delay for loading states

## Fixtures Available

Mock data for common scenarios:
- mockSearchResults - Search API response
- mockRelations - Relations list
- mockInferredRelations - Inferred relations
- mockAnalyticsSummary - Analytics stats
- mockTermsByDomain - Pie chart data
- mockGrowthData - Growth over time
- mockTopTerms - Top terms table
- mockEmptyResults - Empty search results
- mockApiError - Error response

See `/e2e/fixtures/mock-data.ts` for all available fixtures.

## Running Tests

```bash
npm run test:e2e               # Run all tests
npm run test:e2e -- --ui      # Interactive UI
npm run test:e2e:headed       # With browser visible
npm run test:e2e:chromium     # Specific browser
```

## Success Criteria

✅ All 147 tests passing
✅ All CRITICAL tests (45) passing  
✅ No accessibility violations
✅ Tests run < 5 minutes total
✅ All 5 browsers passing

---

For detailed test plan see: `/root/.claude/plans/vast-sauteeing-pnueli.md`
