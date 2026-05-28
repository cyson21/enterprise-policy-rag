# Agent Plan

1. Confirm the active repo state and remaining TODO.
2. Add `docs/runbooks/production-hardening-checklist.md`.
3. Update docs that point at remaining work:
   - `README.md`
   - `TODO.md`
   - `docs/project-tracking.md`
   - `docs/next-agent-bootstrap.md`
   - portfolio guide docs
   - parent project README
4. Run verification without API keys:
   - package manager check
   - frontend smoke/static smoke/build
   - Python compile smoke
   - pytest
   - stale-reference and secret-pattern checks
5. Commit, push, and verify Vercel production deployment.
6. Record changed files, decisions, and verification in this run folder.
