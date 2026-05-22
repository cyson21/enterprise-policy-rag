# Decisions

- Use `DATABASE_URL` as the single switch for runtime PostgreSQL storage.
- Keep no-`DATABASE_URL` behavior unchanged: in-memory repositories and fake providers.
- Put storage selection in `app/runtime.py` instead of embedding it in route setup.
- Let repository constructors own the actual database connections.
- Keep demo seeding tied to `create_app(seed_demo=True)` so portfolio screens still show data in the default in-memory mode.
