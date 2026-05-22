# Decisions

- Use Vercel CLI through `pnpm dlx` instead of installing a global package.
- Deploy the static read-only build to production because it has no API key, Docker, or backend dependency.
- Keep `.vercel` ignored; it contains account/project linkage metadata.
- Leave Git remote/Vercel integration for the next slice because this workspace currently has no configured Git remote.
