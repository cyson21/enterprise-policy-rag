# Agent Plan

1. Add failing API tests for runtime query log behavior:
   - empty Operations metrics start at zero when no logs exist
   - `/retrieve` writes a retrieval query log
   - `/answer` writes an answer query log with token/cost metadata
2. Implement the minimal query log model and repository abstraction.
3. Wire `PolicyRagServices.retrieve` and `PolicyRagServices.answer` to append logs.
4. Change Operations endpoints to read from the service query log repository.
5. Keep demo Operations populated by seeding demo query logs only when `seed_demo=True`.
6. Add PostgreSQL query log schema and repository methods with focused unit tests.
7. Run targeted tests first, then full backend/frontend smoke checks.
8. Update README/TODO/project tracking/bootstrap/API docs and record verification.
