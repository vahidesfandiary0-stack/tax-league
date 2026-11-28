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

## Mandatory execution tracker
Before starting or continuing any RAQTIVA development, read and follow:

- `docs/RELEASE_EXECUTION_TRACKER.md`

That tracker is the permanent project execution record. It defines the mandatory grouped-work approach, group acceptance criteria, production integration gates, evidence requirements, session handoff procedure, and all pre-release and post-release feature groups.

**Mandatory production rule:** Work must be organized into defined groups. Each group must be audited, implemented on a controlled working branch/environment, tested, documented, and explicitly approved by the owner before it is integrated/deployed to the operational server. Never make scattered, untracked, or unapproved production changes. Update the tracker after every meaningful work session and before handing work to another chat.

This policy supersedes any earlier instruction that fixed November 24, 2026 as the project baseline.
