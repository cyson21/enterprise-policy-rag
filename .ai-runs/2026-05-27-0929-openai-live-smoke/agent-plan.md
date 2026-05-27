# Agent Plan

1. Confirm `.env.local` is ignored and store `OPENAI_API_KEY` without committing it.
2. Add failing tests for controlled live smoke skip/guard/execution behavior.
3. Implement `scripts/openai_live_smoke.py`.
4. Run the script first in skip mode and then with `RUN_OPENAI_LIVE_SMOKE=1`.
5. Update README, TODO, project tracking, runbook, and bootstrap docs.
6. Run full backend/frontend verification and git checks.
7. Commit, push, and verify Vercel Git deployment.

