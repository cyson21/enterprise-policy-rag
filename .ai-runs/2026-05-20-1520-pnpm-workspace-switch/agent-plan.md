# Agent Plan

## Context

- The user approved package-manager installation.
- `pnpm` was not initially installed, but `corepack` was available.
- `npm view pnpm version` reported `11.1.3`.

## Steps

- [x] Add a package-manager smoke check that fails without root pnpm workspace config.
- [x] Add root `package.json` with `packageManager: pnpm@11.1.3`.
- [x] Add `pnpm-workspace.yaml`.
- [x] Activate pnpm through corepack.
- [x] Run `pnpm install` and approve required `esbuild` build script.
- [x] Verify pnpm smoke/build and backend regression.
- [x] Update docs and run records.

## Files Expected to Change

- `package.json`
- `pnpm-workspace.yaml`
- `pnpm-lock.yaml`
- `.gitignore`
- `scripts/check-package-manager.mjs`
- `web/package.json`
- `README.md`
- `TODO.md`
- `docs/project-tracking.md`
- `.ai-runs/2026-05-20-1520-pnpm-workspace-switch/*`

## Risks

- pnpm 11 requires explicit build script approval for dependencies such as `esbuild`.
- `node_modules` and `web/dist` must stay untracked.
- Frontend build now depends on installed workspace dependencies.
