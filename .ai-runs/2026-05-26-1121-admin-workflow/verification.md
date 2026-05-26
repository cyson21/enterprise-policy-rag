# Verification

## TDD Red

```bash
pytest tests/test_admin_workflow.py -q
```

Initial result before implementation:

```text
3 failed
```

All failures were 404 responses for missing admin endpoints.

```bash
pnpm web:smoke
```

Initial result before indexing status UI:

```text
missing label: 인덱싱 상태
```

## Targeted Green Checks

```bash
pytest tests/test_admin_workflow.py -q
```

Result:

```text
3 passed
```

```bash
pytest tests/test_postgres_repository.py -q
```

Result:

```text
7 passed
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
69 passed, 2 skipped
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
pnpm web:smoke:static
```

Result:

```text
✓ built
static demo smoke passed
```

```bash
git diff --check
```

Result: passed.
