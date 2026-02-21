# Emulator sync tests (Playwright)

These tests open the localhost emulator and assert that it loads and that the connection state is correct (no stuck hourglass).

## Prerequisites

- **Node.js and npm** (e.g. from [nodejs.org](https://nodejs.org/) or via nvm).

1. Install dependencies from `web-editor`:
   ```bash
   cd web-editor
   npm install
   ```
   This also runs `playwright install chromium` so the Chromium browser is available for tests.

2. If browsers were skipped, install Chromium manually:
   ```bash
   npx playwright install chromium
   ```

3. Serve the emulator (in another terminal):
   ```bash
   cd web-editor
   npm run serve
   ```
   Or: `npx serve htdocs -l 8080`.  
   Or use Docker: `docker compose up -d` then use port 8080.

## Run tests

From `web-editor` (with the emulator already running on port 8080):

```bash
npm run test:emulator
```

Or with a custom URL:

```bash
EMULATOR_URL=http://localhost:3000 npm run test:emulator
```

To watch the browser:

```bash
npm run test:emulator:headed
```

## What is tested

- Page loads and shows the emulator UI (`.container`, `.application`).
- Connection button is visible and not stuck on the orange hourglass (waiting state).
- Live panel is visible and uses the right third of the screen (no blank unused space; width ≥ 200px).
- Live panel shows: CC messages, Tap tempo, Combo (A+B, B+C), and Page ↑/↓ (bank up/down) buttons.
- When a config is loaded, the device display canvas has resolution 240×135 (emulator font scale applied).
