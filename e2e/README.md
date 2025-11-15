# E2E Tests - Playwright

End-to-end tests for Lexikon using Playwright.

## Setup

### First Time Setup

1. Install Playwright browsers:
```bash
npx playwright install
```

2. Start the development server (in a separate terminal):
```bash
npm run dev
```

## Running Tests

### Run All E2E Tests
```bash
npm run test:e2e
```

### Run in UI Mode (Interactive)
```bash
npm run test:e2e:ui
```

### Run in Headed Mode (See Browser)
```bash
npm run test:e2e:headed
```

### Run Specific Browser
```bash
npm run test:e2e:chromium
npm run test:e2e:firefox
npm run test:e2e:webkit
```

### Run Specific Test File
```bash
npx playwright test e2e/auth.spec.ts
npx playwright test e2e/user-journey.spec.ts
```

## Test Files

### `auth.spec.ts` (18 tests)
- Authentication flow (login, register)
- Protected routes redirects
- Form validation
- Accessibility checks

### `user-journey.spec.ts` (19 tests)
- Complete user journeys
- Form validation flows
- OAuth UI elements
- Mobile responsiveness
- Performance checks
- Error handling

## Important Notes

⚠️ **Backend Requirement:**
- E2E tests expect a running backend at `http://localhost:8000`
- Without backend, API calls will fail (expected)
- UI tests will still pass (page rendering, navigation, validation)

⚠️ **Dev Server:**
- Tests require dev server running at `http://localhost:5173`
- Playwright will auto-start if not running
- For manual control, start server first: `npm run dev`

## Test Reports

After running tests, view the HTML report:
```bash
npx playwright show-report
```

## Debugging

### Debug a specific test:
```bash
npx playwright test --debug e2e/auth.spec.ts
```

### Generate screenshots on failure:
Screenshots are automatically saved to `test-results/` on failure.

### View trace files:
```bash
npx playwright show-trace test-results/.../trace.zip
```

## CI/CD

For continuous integration:
```bash
# Install browsers in CI
npx playwright install --with-deps

# Run tests in CI mode (with retries)
CI=true npx playwright test
```

## Browser Coverage

Tests run on:
- ✅ Chromium (Desktop)
- ✅ Firefox (Desktop)
- ✅ WebKit/Safari (Desktop)
- ✅ Mobile Chrome (Pixel 5)
- ✅ Mobile Safari (iPhone 12)

## Documentation

See `docs/TESTING-COMPONENTS-E2E.md` for complete testing strategy.
