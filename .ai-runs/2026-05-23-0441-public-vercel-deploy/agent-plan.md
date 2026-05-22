# Agent Plan

1. Check current Vercel CLI/project state.
2. Use `pnpm dlx vercel` so no global CLI install is required.
3. Run `vercel deploy --yes --prod` from the repository root.
4. Complete device auth if required.
5. Verify deployment state through Vercel API.
6. Verify public URL with HTTP and headless Chrome DOM checks.
7. Update README/TODO/project tracking/bootstrap/runbooks/portfolio docs.
8. Record changed files and verification results.
