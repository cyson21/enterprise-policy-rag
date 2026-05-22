# Verification

## Backend Regression

```bash
pytest -q
```

Result:

```text
58 passed, 2 skipped in 0.34s
```

```bash
python3 -m compileall -q app
```

Result: passed.

## Compose Config

```bash
docker compose config -q
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml config -q
```

Result: both passed.

## Frontend Package and Source Smoke

```bash
node scripts/check-package-manager.mjs
```

Result:

```text
package manager check passed
```

```bash
node scripts/run-web-task.mjs smoke
```

Result:

```text
frontend shell smoke passed
```

## Normal Frontend Build

```bash
node scripts/run-web-task.mjs build
```

Result:

```text
vite v7.3.3 building client environment for production...
1589 modules transformed.
dist/index.html                   0.41 kB
dist/assets/index-KSEwzXp_.css   10.25 kB
dist/assets/index-BwenQmcb.js   225.27 kB
built in 1.03s
```

## Static Demo Build

```bash
node scripts/run-web-task.mjs build:static
```

Result:

```text
vite v7.3.3 building client environment for production...
1589 modules transformed.
dist/index.html                   0.41 kB
dist/assets/index-KSEwzXp_.css   10.25 kB
dist/assets/index-DeHLyZpU.js   225.07 kB
built in 1.01s
```

## Static Browser Smoke

```bash
node scripts/smoke-static-demo.mjs
```

Result:

```text
static demo smoke passed
```

What it checked:

```text
served web/dist locally
opened /?route=operations in headless Chrome
found Enterprise Policy RAG, 공개 데모, 운영 지표, 쿼리 상세, 평가 리포트
observed no /api requests
```

## Public Deployment Attempt

Vercel MCP response:

```text
To deploy this to Vercel, run the Vercel CLI command `vercel deploy`.
Alternatively, use Vercel git integration.
```

Local environment check:

```bash
which vercel || true
find . -maxdepth 3 -path './.vercel/*' -type f
git remote -v
```

Result:

```text
vercel CLI not installed
no .vercel/project.json
no configured Git remote
```

Conclusion: static deploy package is ready, but public URL issuance requires Vercel account authentication or Git remote/Vercel integration.
