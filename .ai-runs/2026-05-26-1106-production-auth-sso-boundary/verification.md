# Verification

## TDD Red

```bash
pytest tests/test_auth_context.py -q
```

Initial result before implementation:

```text
5 failed
```

All failures were 404 responses for missing `/auth/*` endpoints.

```bash
pnpm web:smoke
```

Initial result before frontend auth status:

```text
missing label: getAuthSession
missing label: 권한 세션
```

## Targeted Green Checks

```bash
pytest tests/test_auth_context.py -q
```

Result:

```text
5 passed
```

```bash
pnpm web:smoke
```

Result:

```text
frontend shell smoke passed
```

## Regression Checks

```bash
pytest -q
```

Result:

```text
63 passed, 2 skipped
```

```bash
python3 -m compileall -q app
```

Result: passed.

```bash
pnpm web:build
```

Result:

```text
✓ built
```

```bash
pnpm web:build:static
```

Result:

```text
✓ built
```

```bash
pnpm web:smoke:static
```

Result:

```text
static demo smoke passed
```

```bash
git diff --check
```

Result: passed.
