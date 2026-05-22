# Verification

## Static/Build Checks

Final rerun after Korean UI and screenshot refresh:

```bash
pytest -q
```

Result:

```text
56 passed, 2 skipped
```

```bash
python3 -m compileall -q app
```

Result: passed.

```bash
node scripts/run-web-task.mjs smoke
```

Result:

```text
frontend shell smoke passed
```

```bash
node scripts/run-web-task.mjs build
```

Result:

```text
vite v7.3.3 building client environment for production...
1588 modules transformed.
built in 1.46s
```

## Browser QA

Target flow:

```text
app loads -> Operations nav click -> selected query row renders -> Query Detail panel shows stored evidence.
```

Desktop browser check:

```text
URL: http://127.0.0.1:5173/
Title: Enterprise Policy RAG
Not blank: true
Framework overlay: false
Console error/warn count: 0
Operations console present: true
Query detail panel present: true
Selected query present: true
Trend present: true
Horizontal overflow: false
Korean labels present: true
Top actions clipped: false
```

Desktop layout metrics at screenshot viewport:

```text
viewportWidth: 1752
viewportHeight: 986
horizontalOverflow: false
```

Mobile browser check:

```text
viewportWidth: 356
Operations console present: true
Query detail panel present: true
Selected query present: true
Horizontal overflow: false
Korean labels present: true
```

Mobile detail after scroll:

```text
detail visible: true
detailTop: 10
detailBottom: 399
horizontalOverflow: false
```

Screenshot assets:

```text
docs/assets/operations-demo-ko-v7-desktop.jpg              1440x1650
docs/assets/operations-demo-ko-v12-mobile-overview.jpg     500x1500
docs/assets/operations-demo-ko-v12-mobile-full-page.jpg    500x3600
```

Visual sanity:

```text
operations-demo-ko-v12-mobile-overview.jpg opened and inspected.
The mobile asset is a normal mobile webview capture, not a cropped KPI summary card.
Right-side card and table edges are visible without right-edge clipping.
```

Screenshot capture method:

```text
Browser DOM verification passed for the operations route. Chrome headless window-size screenshots were used for saved assets because Browser screenshot capture timed out in this session and deterministic image dimensions were needed.
Desktop URL: http://127.0.0.1:5173/?route=operations
Mobile webview URL: http://127.0.0.1:5173/?route=operations
```

Cleanup: dev server on port 5173 stopped after final verification.
Note: backend was intentionally not started for screenshot capture; Vite proxy emitted expected `ECONNREFUSED 127.0.0.1:8000` lines while the UI used frontend fallback data.

## Final Regression

```bash
pytest -q
python3 -m compileall -q app
node scripts/run-web-task.mjs smoke
node scripts/run-web-task.mjs build
```

Result:

```text
56 passed, 2 skipped
frontend shell smoke passed
vite build passed
```

Environment cleanup:

```text
No process listening on 127.0.0.1:5173
Colima is not running
```
