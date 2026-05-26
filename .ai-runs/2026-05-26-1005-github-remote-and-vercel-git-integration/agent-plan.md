# Agent Plan

1. Confirm local Git status, current commit, and missing remote.
2. Confirm `cyson21/enterprise-policy-rag` does not already exist.
3. Scan files for obvious token/secret patterns before publishing.
4. Create a public GitHub repository.
5. Add `origin` and push `main`.
6. Attempt `vercel git connect`.
7. Attempt deploy-hook fallback if direct Git connection fails.
8. Update docs and run ledger with completed work and remaining blocker.
9. Commit the documentation/status updates.
