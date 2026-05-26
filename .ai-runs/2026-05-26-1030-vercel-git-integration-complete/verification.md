# Verification

## Pre-check

```bash
git status -sb
pgrep -fl "vercel git connect|vercel.*deploy-hooks|pnpm dlx vercel"
```

Result:

```text
## main...origin/main
No leftover Vercel CLI process.
```

## Vercel Git Connect

```bash
pnpm dlx vercel git connect https://github.com/cyson21/enterprise-policy-rag.git --yes
```

Result:

```text
Retrieving project...
> Connecting GitHub repository: https://github.com/cyson21/enterprise-policy-rag
> cyson21/enterprise-policy-rag is already connected to your project.
```

Note: the command exits non-zero for the already-connected state, but the returned state confirms the repository link exists.

## Project Inspect

```bash
pnpm dlx vercel project inspect enterprise-policy-rag --scope cyson21s-projects
```

Result:

```text
Found Project cyson21s-projects/enterprise-policy-rag
ID: prj_uKUqopQbTxvZq5Z84tDLkpwes7gT
Build Command: node scripts/run-web-task.mjs build:static
Output Directory: web/dist
Install Command: corepack enable pnpm && pnpm install --frozen-lockfile
```

## Deploy Hook Capability Check

```bash
pnpm dlx vercel deploy-hooks list --project enterprise-policy-rag --scope cyson21s-projects
```

Result:

```text
status: ok
projectId: prj_uKUqopQbTxvZq5Z84tDLkpwes7gT
projectName: enterprise-policy-rag
hooks: []
```

This previously failed before Git connection, so the successful list response verifies the project is now Git-connected.
