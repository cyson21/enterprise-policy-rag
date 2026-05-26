# Decisions

- Create the GitHub repository as public because this is a portfolio project and the public Vercel demo is already live.
- Keep `.vercel` ignored and do not commit Vercel project linkage files.
- Do not print or store credential helper tokens.
- Treat Vercel GitHub App access as an account-level browser authorization step because CLI/API attempts cannot grant the app access to the newly created repository from this environment.
