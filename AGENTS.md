# Development and pull request workflow

- Target small-business usability, rapid MVP delivery, and repeatable local Docker testing.
- Use branches and pull requests for changes to `main`; do not bypass required checks.
- Open non-draft pull requests from branches in this repository when ready for CI.
- Owner-authored pull requests are automatically opted into **squash auto-merge** by `.github/workflows/auto-merge.yml`. GitHub must report all required checks successful before the merge.
- The required checks on `main` are `docker-test`, `fixture-tests`, and `build`. Do not delete or silently rename these checks without updating branch protection.
- Approval reviews are not required. Fix failed workflows and merge conflicts; do not attempt to bypass protection.
- Never execute code from an untrusted pull request in a privileged `pull_request_target` job.
- Renovate uses its own rules for compatible dependency updates; major versions and database migrations require deliberate verification.
- Keep `README.md`, `SPRINTS.md`, `BACKLOG.md`, `CONTRIBUTING.md`, and `RELEASES.md` aligned with implemented behavior, and keep badges evidence-based.
- Keep local Docker Compose persistent database volumes intact; never automatically delete production data.
- When adding pages, inherit the shared Deal Radar workspace template and preserve accessible navigation and consistent styling.
