# RAQTIVA Mobile Information Architecture

Status: approved structural plan for implementation
Scope: Android/mobile application navigation and future feature placement
Visual authority: `docs/VISUAL_STANDARD_LOCK.md` and the owner's approved home-screen reference image
Product authority: RAQTIVA project mother document (updated 27 Aban 1405)

## Non-negotiable design constraints

- Keep the approved visual identity: deep navy/royal blue stadium atmosphere, luminous gold frames, Persian RTL typography, official logo and five-item bottom navigation.
- Do not add a sixth bottom-navigation item. New capabilities must be placed inside the five existing destinations.
- Preserve existing working flows while adding navigation.
- A planned feature must be visibly marked as unavailable / in preparation until its real API, permissions, data, and acceptance tests exist. Never simulate scores, XP, duels, lessons, payments, support tickets, or AI answers.
- Paid access must never affect the main league score, rank, exam validity, or XP.
- Founder information remains private and available only after sign-in under Account > About the League > Founder.
- The home screen remains a concise competition dashboard, not a directory of every product capability.

## Global navigation (fixed)

1. **خانه** — personal competition dashboard and concise shortcuts.
2. **آزمون‌ها** — official night exam first; future practice / diagnostic / adaptive exam types are separate and explicitly excluded from the main league unless the owner changes the rules.
3. **رتبه‌بندی** — national and verified-province league tables; XP/levels are shown in a separate panel and never merged with league points.
4. **آکادمی** — question bank learning, Trapology Academy, diagnostic learning, AI tutor, study plan, flashcards, and progress analytics.
5. **اشتراک** — Bazaar plans, purchase, restore, entitlement state, and billing history. Subscription never changes competition fairness.

The account strip on Home opens **حساب کاربری** as a secondary hub. It is not a sixth bottom tab.

## Home screen (keep the approved six-card visual grid)

- Account strip: profile, province verification status, account settings.
- Card 1 — **وضعیت من در لیگ**: official night-exam score/rank only. A future XP indicator may appear as a visually separate secondary metric.
- Card 2 — **آزمون‌های منتشرشده**: published official exams and night-exam entry.
- Card 3 — **تاریخچه نتایج من**: recent finalized results; full history opens from Account.
- Card 4 — **جدول برترین‌ها**: national ranking.
- Card 5 — **برترین‌های استان**: verified-province ranking only.
- Card 6 — **میدان رقابت / دوئل‌ها**: reserved slot for one-to-one duels. Until the duel flow is implemented and tested, show a clear “در حال آماده‌سازی” state and do not allow fake entry.
- **اعتراض‌ها و پشتیبانی** are removed from the Home grid and live under Account > پیگیری و پشتیبانی. The existing appeal flow remains accessible there.

## Destination detail

### 1. آزمون‌ها
- Official night exam (free and unlimited) is the primary action.
- Published official exams, attempt continuation/recovery, finalized results, and exam rules.
- Future separate shelves: practice, daily/weekly learning tests, diagnostic/adaptive tests. Their results must not enter the main league.
- Exam focus mode may suppress nonessential navigation, but must preserve authentication, exam delivery, secure answer saving, finalization, validation, and anti-cheat operations.

### 2. رتبه‌بندی
- Tabs/segmented views: national league and verified province.
- Explain eligibility and tie-break ordering.
- A separate **XP و سطح کاربر** panel is reserved for the post-core milestone. XP is not league score and cannot be purchased.
- Duels, practice, Academy, and paid activity do not affect the league.

### 3. آکادمی
Use one destination with internal sections, not separate bottom tabs:
- بانک سؤالات تخصصی: subject filters, difficulty (hard / very hard / specialist only for public release), source, legal validity date, explanation, and review status.
- آکادمی تله‌شناسی: trap patterns, distractor analysis, timed solving, and learning paths.
- آزمون تشخیصی و تطبیقی: strengths/weaknesses and next-step plan.
- مربی هوشمند: answers grounded in official sources, validity date, confidence, uncertainty, and expert escalation.
- برنامه یادگیری، فلش‌کارت و تحلیل پیشرفت.
- Human review remains mandatory for legal-sensitive content and publication. AI is assistive only.
- Heavy Academy/AI workloads are reduced during night-exam focus mode.

### 4. اشتراک
- Monthly / quarterly / annual Bazaar plans.
- Current entitlement, purchase, restore, pending payment, transaction history, and help.
- Clearly list included Academy/extra-duel entitlements.
- Never sell rank, score, XP, exam priority, or a competitive advantage.

### 5. حساب کاربری (secondary hub)
- Profile and account information.
- Province selection / verification status.
- Exam history and finalized results.
- Appeals and support: existing appeal submissions/status plus future help center, FAQ, and contact/support-ticket channel when implemented.
- About the League.
- Founder introduction (authenticated only).
- Settings, privacy, terms, notification preferences, and sign out.
- No founder data or image on splash, login, registration, OTP, public API, or pre-login pages.

## Future capability placement matrix

| Capability | Permanent destination | Home shortcut |
|---|---|---|
| Night exam | آزمون‌ها | Published exams card |
| National / province league | رتبه‌بندی | Two existing leaderboard cards |
| Duel 1:1 | آزمون‌ها > میدان رقابت / دوئل‌ها | Reserved sixth card |
| Specialist question bank | آکادمی > بانک سؤالات | No separate card |
| Trapology Academy | آکادمی > تله‌شناسی | Academy tab |
| AI tutor | آکادمی > مربی هوشمند | Academy tab |
| Diagnostic / adaptive tests | آزمون‌ها and آکادمی learning path | No extra tab |
| XP / levels | رتبه‌بندی > XP (separate from league) | Small separate profile metric when real |
| Flashcards / study planner | آکادمی | No separate card |
| Appeals / support / FAQ | حساب کاربری > پیگیری و پشتیبانی | Not on Home |
| Founder introduction | حساب کاربری > درباره لیگ > معرفی بنیان‌گذار | Never on public Home |
| Subscription / restore | اشتراک | Existing bottom tab |

## Implementation order and acceptance gates

1. Establish this navigation structure and move appeal/support access to Account without breaking the existing API flow.
2. Build complete destination shells using the approved visual system; future-only sections are clearly unavailable and non-interactive.
3. Connect each feature only when its backend/API and authorization contract are verified.
4. Add automated widget/navigation tests for all destinations, back navigation, login/logout, and focus mode.
5. Run Flutter analyze/tests, build a signed APK, install on physical devices, and verify core flows.
6. Do not merge to `main`, publish, or release without the owner's explicit approval.

## Current known implementation gaps (must not be presented as completed)

- Academy is currently a preparation placeholder.
- Duel is not yet a completed end-to-end feature.
- XP/levels are roadmap items.
- AI tutor and adaptive learning are roadmap items.
- Support center/ticket workflow is not yet implemented.
- Real-device visual validation of the approved home reference remains outstanding.
