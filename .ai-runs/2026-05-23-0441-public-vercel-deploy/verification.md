# Verification

## CLI Availability

```bash
pnpm dlx vercel --version
```

Result:

```text
Vercel CLI 54.3.0
54.3.0
```

## Production Deploy

```bash
pnpm dlx vercel deploy --yes --prod
```

Result:

```text
Linked cyson21s-projects/enterprise-policy-rag
Production https://enterprise-policy-hz4xgjdgs-cyson21s-projects.vercel.app
Aliased https://enterprise-policy-rag.vercel.app
Deployment enterprise-policy-hz4xgjdgs-cyson21s-projects.vercel.app ready.
```

Deployment metadata:

```text
deployment id: dpl_8rEfeFSZUHqSZaBzJdgJ45vUxtrw
inspector: https://vercel.com/cyson21s-projects/enterprise-policy-rag/8rEfeFSZUHqSZaBzJdgJ45vUxtrw
production alias: https://enterprise-policy-rag.vercel.app
```

## Vercel API Check

Tool: `mcp__codex_apps__vercel._get_deployment`

Result:

```text
state: READY
readyState: READY
target: production
project: enterprise-policy-rag
alias: enterprise-policy-rag.vercel.app
```

## HTTP Check

```bash
curl -I -L https://enterprise-policy-rag.vercel.app
```

Result:

```text
HTTP/2 200
server: Vercel
content-type: text/html; charset=utf-8
x-vercel-cache: HIT
```

## Browser DOM Check

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new \
  --disable-gpu \
  --no-first-run \
  --no-default-browser-check \
  --virtual-time-budget=5000 \
  --dump-dom \
  "https://enterprise-policy-rag.vercel.app/?route=operations"
```

Observed labels:

```text
Enterprise Policy RAG
공개 데모
운영 지표
쿼리 상세
평가 리포트
```

## Notes

- Deployment was created from a dirty local working tree, because this repository still has no Git remote and the user asked to proceed.
- `.vercel` was created locally and is ignored by `.gitignore`.
- Follow-up automation should connect Git remote and Vercel Git integration.
