# Verification

## Screenshot Capture

Command:

```bash
pnpm web:build:static
pnpm portfolio:screenshots
```

Result:

```text
captured operations desktop file=docs/assets/operations-demo-ko-v13-desktop.jpg viewport=1440x1650 image=1440x1650 scrollHeight=1650
captured operations mobile webview file=docs/assets/operations-demo-ko-v13-mobile-overview.jpg viewport=500x1400 image=500x1400 scrollHeight=2783
captured operations mobile full page file=docs/assets/operations-demo-ko-v13-mobile-full-page.jpg viewport=500x1500 image=500x2783 scrollHeight=2783
captured knowledge admin desktop file=docs/assets/knowledge-admin-demo-ko-v1-desktop.jpg viewport=1440x1350 image=1440x1350 scrollHeight=1350
portfolio screenshots captured
```

Captured URLs:

- `http://127.0.0.1:<ephemeral>/?route=operations`
- `http://127.0.0.1:<ephemeral>/?route=knowledge&persona=admin-platform`

Dimension check:

```text
operations-demo-ko-v13-desktop.jpg: 1440x1650
operations-demo-ko-v13-mobile-overview.jpg: 500x1400
operations-demo-ko-v13-mobile-full-page.jpg: 500x2783
knowledge-admin-demo-ko-v1-desktop.jpg: 1440x1350
```

Direct image inspection:

- Operations desktop: no right/bottom clipping; metric cards, trend, recent query detail, top evidence, and eval row are visible.
- Operations mobile webview: actual route flow, no focus crop; top navigation is compact, table text fits, and the selected query card ends cleanly.
- Operations mobile full page: captures through the eval section; no right edge clipping or bottom truncation.
- Knowledge admin desktop: admin update/delete controls and audit log are visible; no button/text overflow.

## Command Verification

```bash
pnpm check:package-manager
```

Result: `package manager check passed`

```bash
pnpm web:build:static
```

Result: Vite static production build succeeded.

```bash
pnpm portfolio:screenshots
```

Result: all four portfolio screenshots captured; no `/api` requests were made by the static build.

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

Result: `76 passed, 2 skipped in 1.00s`

```bash
git diff --check
```

Result: exit code 0.

```bash
git diff -- . ':(exclude).env.local' | rg -n "sk-proj|OPENAI_API_KEY=.*sk-|xox[baprs]-|ghp_[A-Za-z0-9]|vercel_[A-Za-z0-9]" || true
```

Result: no matches.

```bash
rg -n "operations-demo-ko-v7|operations-demo-ko-v12|Portfolio screenshot refresh after final feature set|refresh portfolio screenshots after the final feature set" README.md TODO.md docs /Users/chanyang.son/Documents/side-projects/projects/02-enterprise-policy-rag/README.md || true
```

Result: no stale current-doc screenshot references.

## Git and Deployment

```bash
git commit -m "Docs: 포트폴리오 스크린샷 최종화"
git push origin main
```

Result: pushed `0264faf` to `origin/main`.

```bash
pnpm dlx vercel ls enterprise-policy-rag --scope cyson21s-projects
pnpm dlx vercel inspect https://enterprise-policy-k7zx1o7e7-cyson21s-projects.vercel.app --scope cyson21s-projects
curl -I -L https://enterprise-policy-rag.vercel.app
curl -s -L https://enterprise-policy-rag.vercel.app | rg -n "Enterprise Policy RAG|assets/index-DzMGZ5wQ"
```

Result:

- Latest deployment: `dpl_FeF8xphSrHCRrpht5S8Ef5djqSeJ`
- Deployment status: `Ready`
- Production alias: `https://enterprise-policy-rag.vercel.app`
- Production HTTP status: `HTTP/2 200`
- Served static asset hash includes `assets/index-DzMGZ5wQ.css`
