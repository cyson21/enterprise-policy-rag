# Verification

## Commands

```bash
pnpm check:package-manager
```

Result: `package manager check passed`

```bash
pnpm web:build:static
```

Result: Vite static production build succeeded.

```bash
pnpm web:smoke:static
```

Result: `static demo smoke passed`

```bash
pnpm web:smoke
```

Result: `frontend shell smoke passed`

```bash
python3 -m compileall -q app scripts/openai_live_smoke.py
```

Result: exit code 0.

```bash
pytest -q
```

Result: `76 passed, 2 skipped in 1.49s`

```bash
git diff --check
```

Result: exit code 0.

```bash
git diff -- . ':(exclude).env.local' | rg -n "sk-proj|OPENAI_API_KEY=.*sk-|xox[baprs]-|ghp_[A-Za-z0-9]|vercel_[A-Za-z0-9]" || true
```

Result: no matches.

```bash
rg -n 'Next Valuable Slice|\[ \]|dpl_8rEfe|Portfolio screenshot refresh after final feature set|refresh portfolio screenshots after the final feature set' TODO.md docs README.md /Users/chanyang.son/Documents/side-projects/projects/02-enterprise-policy-rag/README.md || true
```

Result: only the TODO status legend matched `[ ]`; no incomplete work item or stale deployment/screenshot reference matched.

Forbidden-terminology scan over README, TODO, docs, this run folder, and the parent project README.

Result: no matches in source docs.

## Closeout Check

- `TODO.md` has no unchecked project work items.
- `docs/project-tracking.md` states that there is no remaining Project 02 portfolio-scope work.
- `docs/next-agent-bootstrap.md` points any future production SaaS rollout to `docs/runbooks/production-hardening-checklist.md`.
- Default verification remains API-key-free and Docker-free.

## Git and Deployment

```bash
git commit -m "Docs: 프로덕션 보강 체크리스트 추가"
git push origin main
pnpm dlx vercel ls enterprise-policy-rag --scope cyson21s-projects
pnpm dlx vercel inspect <latest-production-deployment-url> --scope cyson21s-projects
curl -I -L https://enterprise-policy-rag.vercel.app
```

Result:

- Commit pushed to `origin/main`.
- Vercel Git integration created a production deployment and reported `Ready`.
- Production alias `https://enterprise-policy-rag.vercel.app` returned `HTTP/2 200`.
- The served static HTML still includes the `Enterprise Policy RAG` title and the expected built asset hash.
