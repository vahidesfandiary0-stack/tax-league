# RAQTIVA — Project Baseline Policy

## Permanent rule
The development baseline must always be the latest valid and verified project version available at the time work begins.

- No fixed calendar date, commit, release, branch, or historical build is a permanent baseline.
- The November 24, 2026 version is not a mandatory baseline.
- Before every development task, inspect the latest server state, GitHub branches and commits, and the latest valid web and Android releases.
- Identify the newest valid and compatible source state using verifiable evidence.
- Apply only explicitly approved changes on top of that baseline.
- Preserve existing data, production stability, and unrelated changes.
- Never overwrite newer work with an older snapshot merely because the older snapshot was previously selected.
- Do not merge into the main or release branch, deploy, or publish a release without explicit approval.

This policy supersedes any earlier instruction that fixed November 24, 2026 as the project baseline.

## Recorded working baseline — November 28, 2026

For the next approved development work, the selected verified source candidate is:

- **Commit:** `9f16d99e247081cec980e8923f750ec27e6f7417`
- **Branch:** `release/raqtiva-finalize-20261127`
- **Verification runs:** GitHub Actions runs `45899619657` (Release backend verification), `45899619673` (Web PWA build), and `45899619743` (Android signed release).
- **Observed result:** all three runs concluded successfully on 2026-11-26 at 21:39:20 UTC, with event `pull_request`.

### Scope and limitations of this record

- This records `9f16d99` as the **working source baseline candidate** because it is newer than the previously compared `8127592` candidate and has successful backend, web, and Android validation evidence.
- The newer `672d7d188e95a93ce7f47aa6bef163f851cf946b` candidate has successful Android `push` runs, but the inspected run list did not show corresponding Web PWA or backend verification runs. It is therefore not established by the available evidence as a complete web-and-Android baseline.
- No GitHub Release was found, and the GitHub Deployments query returned no deployments. Thus this record does **not** claim that `9f16d99` was formally published or deployed to production.
- The current `/opt/tax-league` checkout was found on the older `mobile/ui-redesign-20261119` branch at `cd869feaa53041be7e44da3ea058e6fa0b165206`, with extensive local modifications and untracked files. It must not be reset, cleaned, checked out over, or pulled over as part of baseline selection.
- Before implementation, re-check whether any newer compatible candidate or release evidence has appeared. This recorded baseline does not override the permanent latest-verified-version rule above.

No merge to `main`, production deployment, or public release is authorized by this record.
