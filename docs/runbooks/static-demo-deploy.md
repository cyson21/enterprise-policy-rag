# Static Demo Deploy Runbook

Date: 2026-05-23

## Goal

Deploy a public read-only portfolio demo without API keys, Docker, PostgreSQL, or a backend process.

The static demo uses the same React UI, but `VITE_DEMO_MODE=static` makes the frontend use deterministic fake-provider fixtures instead of calling `/api`.

## Production URL

```text
https://enterprise-policy-rag.vercel.app
```

GitHub repository:

```text
https://github.com/cyson21/enterprise-policy-rag
```

Deployment:

```text
dpl_8rEfeFSZUHqSZaBzJdgJ45vUxtrw
```

## Local Build

From the repository root:

```bash
node scripts/run-web-task.mjs build:static
```

Output:

```text
web/dist
```

## Static Smoke

Run the headless browser smoke after the static build:

```bash
node scripts/smoke-static-demo.mjs
```

This script serves `web/dist`, opens the Operations route in headless Chrome, checks key Korean demo labels, and fails if the page requests `/api`.

Expected result:

```text
static demo smoke passed
```

## Local Preview

```bash
node scripts/run-web-task.mjs preview:static
```

Open:

```text
http://127.0.0.1:4173/?route=operations
```

The top bar should show `공개 데모` and `fake 제공자`.

## Vercel

The repository includes `vercel.json`:

```json
{
  "buildCommand": "node scripts/run-web-task.mjs build:static",
  "installCommand": "corepack enable pnpm && pnpm install --frozen-lockfile",
  "outputDirectory": "web/dist"
}
```

Deploy with one of these paths:

1. Vercel CLI from the repository root:

```bash
vercel deploy
```

2. Vercel Git integration:

```text
Import the Git repository, keep the repository root as the project root, and let vercel.json control the build/output settings.
```

## Current Deployment Notes

The first production deployment was created through the Vercel CLI after device auth.

```text
Project: cyson21s-projects/enterprise-policy-rag
Production alias: https://enterprise-policy-rag.vercel.app
Inspector: https://vercel.com/cyson21s-projects/enterprise-policy-rag/8rEfeFSZUHqSZaBzJdgJ45vUxtrw
```

The local `.vercel` directory is intentionally ignored by Git.

## Automatic Deployment Status

The GitHub repository exists and `main` has been pushed. Direct Vercel Git connection is not complete yet.

Attempted:

```bash
pnpm dlx vercel git connect https://github.com/cyson21/enterprise-policy-rag.git --yes
```

Result:

```text
Failed to connect cyson21/enterprise-policy-rag to project.
```

Deploy-hook fallback was also attempted, but Vercel only allows deploy hooks after the project is connected to a Git repository.

Next action:

```text
Open Vercel Project Settings -> Git and grant the Vercel GitHub App access to cyson21/enterprise-policy-rag.
```
