# Changed Files

## Backend

- `app/providers.py`
  - Added `OpenAIHTTPTransport` for explicit opt-in Responses API calls.
  - Kept `LLM_PROVIDER=fake` as the default path.
  - Parses `output_text` first and message content text as a fallback.
  - Converts OpenAI HTTP/network errors into clear runtime errors.

## Tests

- `tests/test_provider_selection.py`
  - Added mock HTTP opener tests for request method, endpoint, headers, body, output parsing, and error handling.
  - Updated provider selection tests for the live transport path.

## Docs

- `README.md`
  - Updated current implementation and remaining work.
  - Added the portfolio interview guide link.
- `TODO.md`
  - Marked live OpenAI transport complete.
  - Added remaining extension candidates.
- `docs/project-tracking.md`
  - Added Phase 4B snapshot and updated remaining work.
- `docs/next-agent-bootstrap.md`
  - Updated next-agent scope after OpenAI transport.
- `docs/api-data-model.md`
  - Updated provider selection table.
- `docs/runbooks/local-demo.md`
  - Documented optional OpenAI provider check.
- `docs/portfolio-one-pager.md`
  - Updated boundaries and next slice.
- `docs/portfolio-interview-guide.md`
  - Added demo path, architecture story, tradeoffs, evidence links, and next steps.

## Run Ledger

- `.ai-runs/2026-05-22-1812-phase4b-openai-and-portfolio-closeout/goal.md`
- `.ai-runs/2026-05-22-1812-phase4b-openai-and-portfolio-closeout/agent-plan.md`
- `.ai-runs/2026-05-22-1812-phase4b-openai-and-portfolio-closeout/decisions.md`
- `.ai-runs/2026-05-22-1812-phase4b-openai-and-portfolio-closeout/changed-files.md`
- `.ai-runs/2026-05-22-1812-phase4b-openai-and-portfolio-closeout/verification.md`

## Side-Projects Hub

- `/Users/chanyang.son/Documents/side-projects/projects/02-enterprise-policy-rag/README.md`
  - Updated the local portfolio hub summary and screenshot/doc links.
