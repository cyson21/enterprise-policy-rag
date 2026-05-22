# Goal

Add query trend metrics to Operations using persisted query logs.

Scope:

- Add `GET /metrics/trend`.
- Aggregate retrieval count, answer count, zero-result count, and average latency by date.
- Display the trend in the Operations screen.
- Keep normal verification API-key-free and Docker-free.
