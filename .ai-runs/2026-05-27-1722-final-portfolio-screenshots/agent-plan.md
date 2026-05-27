# Agent Plan

## Context

- Parent screenshot guide: `/Users/chanyang.son/Documents/side-projects/portfolio_screenshot_capture_guide.md`
- Repo: `/Users/chanyang.son/Documents/side-projects/repos/enterprise-policy-rag`
- Browser validation path: headless CLI capture, because the user previously asked not to show side-project browser work on screen.
- Static demo mode: `VITE_DEMO_MODE=static`, no `/api` calls, fake-provider fixtures.

## Steps

1. Rebuild the static frontend bundle from source.
2. Add a reusable headless screenshot capture script for static portfolio assets.
3. Capture:
   - Operations desktop
   - Operations mobile webview
   - Operations mobile full page, sized from the actual document height
   - Knowledge Library admin desktop
4. Inspect the generated image files directly for clipping, text fit, and full-page bottom coverage.
5. Update docs to reference the new assets and remove the screenshot-refresh item from remaining work.
6. Run verification:
   - static build
   - screenshot capture
   - static demo smoke
   - package manager check
   - backend tests/compile smoke as needed for closeout confidence
   - git diff/secret guard
7. Record changed files, decisions, and verification output in this run folder.
