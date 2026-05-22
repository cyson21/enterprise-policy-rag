# Decisions

- Keep the default app path on the in-memory repository and fake embedding provider so local tests remain API key-free.
- Add document list/detail as retrieval-core API, not as an answer-generation surface.
- Require `workspace_id` on document list/detail reads and return `404` when the document belongs to another workspace.
- Return `embedding_dimensions` in chunk preview, but do not expose raw embedding vectors through the UI API.
- Keep Knowledge Library read-oriented for this slice: live document list, selected detail, owner/source/content type, and chunk previews.
- Preserve fixture fallback in the frontend client so the screen still renders if the backend is temporarily unavailable.
