# Changed Files

- `.gitignore`: added `.env.local` so local API keys are never staged.
- `scripts/openai_live_smoke.py`: added opt-in OpenAI live smoke with `.env.local` loading, in-memory seeded data, safe metadata output, and SSL cert fallback via `certifi` when available.
- `tests/test_openai_live_smoke.py`: added tests for skip-by-default behavior, key guard, OpenAI provider forcing, database avoidance, seeded answer flow, and secret-safe output.
- `README.md`: documented controlled live smoke while preserving fake-provider default verification.
- `TODO.md`: marked controlled live OpenAI smoke complete.
- `docs/project-tracking.md`: added Phase 5E snapshot and moved remaining work to portfolio polish/hardening.
- `docs/next-agent-bootstrap.md`: added this run and updated next recommended work.
- `docs/runbooks/local-demo.md`: added bounded OpenAI live smoke command and updated expected test count.
- `docs/api-data-model.md`: documented controlled live smoke command and secret handling.
- `docs/portfolio-one-pager.md`: updated OpenAI boundary and next-slice guidance.
- `docs/portfolio-interview-guide.md`: updated OpenAI tradeoff and next steps.
- `/Users/chanyang.son/Documents/side-projects/projects/02-enterprise-policy-rag/README.md`: updated side-project hub summary outside this git repo.
