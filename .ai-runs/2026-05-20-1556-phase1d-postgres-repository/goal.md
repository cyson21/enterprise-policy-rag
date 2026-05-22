# Goal

Add a PostgreSQL repository path for the retrieval core while preserving the no-key, fake-provider, in-memory default used by tests and local UI development.

## Scope

- Define a repository interface shared by in-memory and PostgreSQL implementations.
- Implement PostgreSQL persistence for workspaces, documents, and document chunks.
- Map joined document/chunk rows back into retrieval-ready models.
- Verify the repository with fake connection tests so CI does not require a running database.

## Out of Scope

- Switching the default app factory to PostgreSQL.
- Network dependency installation.
- OpenAI API integration.
- Answer generation and eval.
