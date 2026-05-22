# Agent Plan

## Context

- Search Console already calls live `/api/retrieve`.
- Retrieval Lab is still a static preview.
- Existing `loadRetrieval` client supports `topK` and `scoreThreshold`.

## Steps

- [x] Add failing frontend smoke markers for Retrieval Lab live controls.
- [x] Implement live Retrieval Lab state for query, top-k, score threshold, and selected result.
- [x] Reuse typed retrieval client and active persona from app shell.
- [x] Add compact controls and debug metadata display without adding answer generation.
- [x] Run frontend smoke/build, backend tests, compile smoke, compose config, and browser smoke.
- [x] Update README, TODO, project tracking, next-agent bootstrap, changed-files, decisions, and verification.

## Risks

- UI must stay retrieval-only and not imply generated answers.
- Controls should not resize or shift the layout.
- `score_threshold` should visibly affect result filtering.
