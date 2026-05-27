# Decisions

## Headless Capture

Use headless Chrome through a repo script instead of an interactive browser session. The Browser plugin is available, but the user previously asked that side-project browser work not be visible while they are working. Headless capture also makes the screenshot flow repeatable.

## Asset Naming

Use new `v13` Operations screenshot filenames instead of overwriting previous assets, following the parent screenshot guide's cache-avoidance rule.

## Screenshot Set

Keep Operations as the primary portfolio evidence because it summarizes query logging, latency, cost, query detail, evidence, and eval. Add one Knowledge Library admin desktop screenshot because the latest implemented feature set includes document update/delete/audit controls that were not visible in the previous screenshot set.

## Mobile Overview Height

Use a 500x1400 mobile webview screenshot instead of 500x1500. At 1500px the next query card began at the bottom edge, which looked like a clipped card. The 1400px viewport still shows the route's first meaningful mobile flow and ends after the selected query row.

## CSS Polish

Make table `small` metadata display on its own line so source URIs and subtitles do not visually attach to titles. Compress mobile navigation into a two-column grid so the mobile screenshots expose more of the actual product screen without using a crop or focus route.
