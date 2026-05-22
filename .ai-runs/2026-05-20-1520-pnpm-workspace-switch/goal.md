# Goal

## Objective

Switch the frontend package manager from npm-oriented commands to pnpm workspace management.

## Scope

In scope:

- Root pnpm workspace configuration.
- pnpm lockfile generation.
- Root scripts for web dev/build/smoke.
- Package-manager smoke check.
- Documentation updates.

Out of scope:

- Frontend feature changes.
- Backend feature changes.
- OpenAI/API provider changes.

## Exit Criteria

- `pnpm@11.1.3` is active.
- `pnpm install` produces a lockfile.
- `pnpm web:smoke` and `pnpm web:build` pass.
- Existing backend tests still pass.
