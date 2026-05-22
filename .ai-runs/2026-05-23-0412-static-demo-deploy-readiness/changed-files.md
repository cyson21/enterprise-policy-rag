# Changed Files

## Frontend

- `web/src/config/demoMode.ts`
  - Added `isStaticDemoMode` from `VITE_DEMO_MODE=static`.
- `web/src/vite-env.d.ts`
  - Added Vite env type reference.
- `web/src/api/client.ts`
  - Short-circuits API calls to deterministic fixtures in static demo mode.
- `web/src/app/App.tsx`
  - Shows `public-demo` environment in static demo mode.
- `web/src/utils/display.ts`
  - Formats `public-demo` as `공개 데모`.
- `web/scripts/smoke.mjs`
  - Adds static demo labels to source smoke coverage.

## Scripts and Deploy Config

- `scripts/run-web-task.mjs`
  - Added `build:static` and `preview:static`.
- `scripts/smoke-static-demo.mjs`
  - Added a headless Chrome smoke that serves `web/dist`, renders Operations, and fails on `/api` requests.
- `scripts/check-package-manager.mjs`
  - Verifies the new static demo scripts.
- `package.json`
  - Added `web:build:static`, `web:preview:static`, and `web:smoke:static`.
- `vercel.json`
  - Added static demo build command and `web/dist` output directory.

## Docs

- `docs/runbooks/static-demo-deploy.md`
  - Added static build, smoke, preview, Vercel deploy, and limitation notes.
- `README.md`
- `TODO.md`
- `docs/project-tracking.md`
- `docs/next-agent-bootstrap.md`
- `docs/runbooks/local-demo.md`
- `docs/portfolio-one-pager.md`
- `docs/portfolio-interview-guide.md`
  - Updated with static demo readiness and remaining public URL dependency.

## Run Ledger

- `.ai-runs/2026-05-23-0412-static-demo-deploy-readiness/goal.md`
- `.ai-runs/2026-05-23-0412-static-demo-deploy-readiness/agent-plan.md`
- `.ai-runs/2026-05-23-0412-static-demo-deploy-readiness/decisions.md`
- `.ai-runs/2026-05-23-0412-static-demo-deploy-readiness/changed-files.md`
- `.ai-runs/2026-05-23-0412-static-demo-deploy-readiness/verification.md`

## Side-Projects Hub

- `/Users/chanyang.son/Documents/side-projects/projects/02-enterprise-policy-rag/README.md`
  - Updated static deploy status.
