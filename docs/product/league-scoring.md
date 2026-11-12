# League scoring and ranking

## Rules
- Only finalized attempts for exams with `counts_for_league=True` enter the league.
- Each attempt has at most one immutable `LeagueScoreEntry` (database OneToOne constraint).
- The entry is created inside the same transaction that finalizes the attempt.
- Daily practice exams must keep `counts_for_league=False`; official season exams set it to true.
- A matching active season must cover both the attempt start and submission timestamps.

## Ranking
Aggregate score descending, then total correct answers descending, total wrong answers ascending, total elapsed seconds ascending, and stable user ID as final deterministic ordering. No phone number is exposed. A blank display name is shown as "کاربر".

## API
- `GET /api/v1/league/season/` active season metadata
- `GET /api/v1/league/leaderboard/` current leaderboard
- `GET /api/v1/league/leaderboard/?season=<uuid>` leaderboard for a selected active/closed season
- `GET /api/v1/league/me/` current user's rank and totals

All endpoints require authentication. Admins create a season in draft, then activate it in Django admin. Do not edit active/closed seasons; create a new season for corrections under a documented governance process.

## Operational notes
This is an initial ledger and aggregation implementation, not a tested production release. Before launch, add audited season activation/closure actions, tie-resolution policy, appeal adjustments as separate compensating ledger records, and load/concurrency tests on PostgreSQL. Never edit or delete a recorded score entry to resolve an appeal.
