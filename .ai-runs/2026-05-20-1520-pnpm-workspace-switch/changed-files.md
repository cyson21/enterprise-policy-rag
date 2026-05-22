# Changed Files

| File | Purpose |
|---|---|
| `package.json` | Root pnpm workspace scripts and `packageManager` pin |
| `pnpm-workspace.yaml` | Declare `web` as a workspace package and allow reviewed `esbuild` build script |
| `pnpm-lock.yaml` | Lock frontend dependencies through pnpm |
| `.gitignore` | Ignore Node install/build artifacts |
| `scripts/check-package-manager.mjs` | Verify root pnpm workspace configuration and esbuild build approval |
| `web/package.json` | Keep web scripts under pnpm workspace and move build tools to dev dependencies |
| `README.md` | Replace npm commands with pnpm commands |
| `TODO.md` | Record pnpm workspace switch |
| `docs/project-tracking.md` | Record package-manager decision and verification |
