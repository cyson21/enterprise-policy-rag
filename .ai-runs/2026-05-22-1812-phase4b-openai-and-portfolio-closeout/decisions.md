# Decisions

- Use the OpenAI Responses API path for live completion because current OpenAI docs describe it as the direct text generation interface.
- Reference checked: https://developers.openai.com/api/docs/guides/text and https://platform.openai.com/docs/api-reference/responses.
- Keep the transport in the Python standard library (`urllib`) so the project does not add a new runtime dependency for an optional path.
- Parse `output_text` first and fall back to message content items so tests can tolerate common Responses API response shapes.
- Do not run an external OpenAI request in this phase; tests use injected fake HTTP openers.
- Keep `LLM_PROVIDER=fake` as the default and require `OPENAI_API_KEY` for `LLM_PROVIDER=openai`.
