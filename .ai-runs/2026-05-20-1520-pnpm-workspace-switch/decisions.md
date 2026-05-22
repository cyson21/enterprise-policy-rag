# Decisions

| Decision | Reason | Alternatives |
|---|---|---|
| Use pnpm 11.1.3 | Current latest version and better workspace/lockfile fit than npm for this repo | npm, Bun, Yarn classic |
| Use corepack to activate pnpm | Avoid global npm install and keep package manager pinned | `npm install -g pnpm` |
| Add root workspace scripts | Keep commands consistent from repository root | Run all commands from `web/` |
| Approve `esbuild` build script | Vite depends on esbuild and pnpm 11 blocks unapproved build scripts | Leave build broken |
| Commit `allowBuilds.esbuild` in workspace config | Keeps fresh installs reproducible under pnpm 11 security defaults | Rely on local user config |
