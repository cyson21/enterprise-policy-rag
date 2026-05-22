# Decisions

| Decision | Reason | Alternatives |
|---|---|---|
| Declare frontend dependencies without installing them | Network package installation was not explicitly approved | Run `npm install` immediately |
| Add no-install frontend smoke script | Gives fast structural verification before dependency install | Rely only on manual file review |
| Add `/workspaces/current` and `/personas` before retrieval UI wiring | App shell needs workspace/persona context first | Hard-code all context only in frontend |
| Use static route previews for Phase 1A | This slice is shell/persona foundation, not live retrieval wiring | Implement Search Console API integration now |
| Keep first screen as Search Console | Master plan requires no marketing landing page | Start with dashboard or intro page |
