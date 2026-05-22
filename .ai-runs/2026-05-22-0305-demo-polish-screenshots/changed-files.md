# Changed Files

## Frontend

- `web/src/utils/display.ts`
  - Added Korean display formatters for workspace labels, provider, users, departments, visibility, access reasons, document titles, query labels, and eval document ids.
- `web/src/app/routes.tsx`
  - Switched route labels to Korean.
- `web/src/app/App.tsx`
  - Added `route` and `persona` query parameter bootstrapping for deterministic screenshot capture.
- `web/src/components/layout/AppShell.tsx`
  - Formats workspace environment/provider labels in Korean.
- `web/src/components/persona/PersonaSelector.tsx`
  - Shows Korean user and department labels.
- `web/src/fixtures/personas.ts`
  - Normalized the local workspace provider value to `fake` for frontend display formatting.
- `web/src/routes/search/SearchPage.tsx`
  - Localized visible Search UI labels and metadata display.
- `web/src/routes/knowledge/KnowledgePage.tsx`
  - Localized visible Knowledge UI labels and metadata display.
- `web/src/routes/retrieval-lab/RetrievalLabPage.tsx`
  - Localized visible Retrieval Lab labels and metadata display.
- `web/src/routes/operations/OperationsPage.tsx`
  - Reworked Operations into a two-column console, localized visible labels, and added `focus=query-detail` / `focus=mobile-summary` support for deterministic screenshot capture.
- `web/src/styles/tokens.css`
  - Added operations console layout, sticky detail panel, responsive overflow guards, table containment, top bar wrapping, mobile persona label fixes, and screenshot focus styling.
- `web/scripts/smoke.mjs`
  - Updated required smoke labels for the Korean interface and display formatter.

## Screenshot Assets

- `docs/assets/operations-demo-desktop.jpg`
- `docs/assets/operations-demo-mobile.jpg`
- `docs/assets/operations-demo-mobile-detail.jpg`
- `docs/assets/operations-demo-ko-v7-desktop.jpg`
- `docs/assets/operations-demo-ko-v12-mobile-overview.jpg`
- `docs/assets/operations-demo-ko-v12-mobile-full-page.jpg`

## Docs

- `README.md`
- `TODO.md`
- `docs/project-tracking.md`
- `docs/next-agent-bootstrap.md`
- `docs/runbooks/local-demo.md`
- `docs/portfolio-one-pager.md`
