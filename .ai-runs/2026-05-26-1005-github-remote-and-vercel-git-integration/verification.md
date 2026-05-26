# Verification

## Existing Repository Check

```bash
git ls-remote https://github.com/cyson21/enterprise-policy-rag.git
```

Initial result:

```text
remote: Repository not found.
fatal: repository 'https://github.com/cyson21/enterprise-policy-rag.git/' not found
```

## Secret Pattern Scan

```bash
rg -n "github_pat_|ghp_|OPENAI_API_KEY=|sk-[A-Za-z0-9]|BEGIN (RSA|OPENSSH|PRIVATE)|VERCEL_TOKEN|password=" \
  --glob '!node_modules/**' \
  --glob '!web/node_modules/**' \
  --glob '!web/dist/**' \
  --glob '!.vercel/**' .
```

Result:

```text
Only dummy `sk-test` test values and `<redacted>` documentation examples were found.
```

## GitHub Repository Creation

Created:

```text
full_name: cyson21/enterprise-policy-rag
html_url: https://github.com/cyson21/enterprise-policy-rag
private: false
default_branch: main
```

GitHub MCP verification:

```text
repository_full_name: cyson21/enterprise-policy-rag
visibility: public
default_branch: main
clone_url: https://github.com/cyson21/enterprise-policy-rag.git
```

## Push Verification

```bash
git remote add origin https://github.com/cyson21/enterprise-policy-rag.git
git push -u origin main
git ls-remote origin refs/heads/main
```

Result:

```text
main -> main
branch 'main' set up to track 'origin/main'
96c5663bcc597c017fae6fa37018ebe35741461a refs/heads/main
```

## Vercel Git Integration Attempt

```bash
pnpm dlx vercel git connect https://github.com/cyson21/enterprise-policy-rag.git --yes
```

Result:

```text
Failed to connect cyson21/enterprise-policy-rag to project.
Make sure there aren't any typos and that you have access to the repository if it's private.
```

## Deploy Hook Fallback Attempt

```bash
pnpm dlx vercel deploy-hooks create github-main-auto-deploy --ref main --project prj_uKUqopQbTxvZq5Z84tDLkpwes7gT --scope team_CNHWWzmMOiIVls49oNpioW2O
```

Result:

```text
This project is not connected to a Git repository, so it cannot have deploy hooks.
Connect a repo under Project Settings -> Git.
```

## Public Demo Check

```bash
curl -I -L https://enterprise-policy-rag.vercel.app
```

Result:

```text
HTTP/2 200
server: Vercel
x-vercel-cache: HIT
```

## Working Tree Check

```bash
git diff --check
```

Result: passed.

## Remaining Blocker

Vercel GitHub App must be granted access to `cyson21/enterprise-policy-rag` in the browser before Vercel can connect the repo for push-based automatic deployments.
