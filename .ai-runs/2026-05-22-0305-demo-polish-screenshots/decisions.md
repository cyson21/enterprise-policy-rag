# Decisions

- Focus polish on Operations because it best demonstrates backend depth: metrics, trend, query logs, evidence, eval, and provider boundaries.
- Do not add a marketing landing page.
- Keep visual changes source-only in React/CSS.
- Prefer Browser plugin validation; do not add a heavy browser automation dependency unless the screenshot blocker remains material.
- Localize the demo interface in the frontend display layer so backend seed data and backend tests can stay stable.
- Use a two-line top bar and a cropped mobile detail asset to prevent screenshot edge clipping in portfolio previews.
- Replace the portfolio board's mobile summary source with a dedicated KPI card capture instead of scaling a full mobile page into a small side panel.
- Drop the composite portfolio board from the documented screenshot set and keep desktop/mobile captures as separate image assets.
