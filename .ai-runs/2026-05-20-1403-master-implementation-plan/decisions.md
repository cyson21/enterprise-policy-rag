# Decisions

| Decision | Reason | Alternatives |
|---|---|---|
| Create a separate master plan instead of expanding the architecture doc | The architecture doc explains direction, while implementation needs phase, file, API, and verification detail | Keep all planning in one long architecture document |
| Use vertical slices as the execution unit | Each slice produces a visible demo outcome and matching backend support | Implement backend layers first and UI later |
| Make Phase 1A frontend shell the next immediate work | The user explicitly needs visible portfolio screens | Continue PostgreSQL persistence before UI |
| Keep OpenAI adapter after fake answer/citation | API-key-free demo and CI are still core requirements | Start with live OpenAI integration |
| Put demo data and persona scenarios in the plan | Portfolio proof needs repeatable visible scenarios | Leave demo data to ad hoc manual setup |
