# Verification

## Commands

```bash
npm view pnpm version
corepack enable pnpm && pnpm --version
pnpm install
pnpm approve-builds esbuild
pnpm install
pnpm install --frozen-lockfile
pnpm check:package-manager
pnpm web:smoke
pnpm --filter enterprise-policy-rag-web exec tsc -b
pnpm web:build
pytest -q
python3 -m compileall -q app
docker compose config -q
curl -I --max-time 5 http://127.0.0.1:5173/
Browser DOM smoke for `Search Console`, `Mina Kim / security`, `Operations`
```

## Result

- Latest pnpm resolved through npm registry: `11.1.3`.
- `pnpm --version`: `11.1.3`.
- `pnpm install`: passed after approving `esbuild`.
- `pnpm install --frozen-lockfile`: passed with workspace `allowBuilds.esbuild`.
- `pnpm check:package-manager`: passed.
- `pnpm web:smoke`: passed.
- `pnpm --filter enterprise-policy-rag-web exec tsc -b`: passed.
- `pnpm web:build`: passed.
- `pytest -q`: passed with 11 tests.
- `python3 -m compileall -q app`: passed.
- `docker compose config -q`: passed.
- Dev server responded `HTTP/1.1 200 OK` at `http://127.0.0.1:5173/`.
- Browser DOM smoke found `Search Console`, `Mina Kim / security`, and `Operations`.
