# Verification

## Targeted Provider Test

```bash
pytest tests/test_provider_selection.py -q
```

Result:

```text
8 passed in 0.10s
```

## Full Backend Test Suite

```bash
pytest -q
```

Result:

```text
58 passed, 2 skipped in 0.20s
```

## Python Compile Smoke

```bash
python3 -m compileall -q app
```

Result: passed.

## Compose Config

```bash
docker compose config -q
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml config -q
```

Result: both passed.

## Package Manager Check

```bash
node scripts/check-package-manager.mjs
```

Result:

```text
package manager check passed
```

## Frontend Smoke

```bash
node scripts/run-web-task.mjs smoke
```

Result:

```text
frontend shell smoke passed
```

## Frontend Build

```bash
node scripts/run-web-task.mjs build
```

Result:

```text
vite v7.3.3 building client environment for production...
1588 modules transformed.
dist/index.html                   0.41 kB
dist/assets/index-KSEwzXp_.css   10.25 kB
dist/assets/index-54BSgILW.js   225.24 kB
built in 939ms
```

## External Calls

No real OpenAI request was executed. Live transport behavior was verified with injected fake HTTP openers only.
