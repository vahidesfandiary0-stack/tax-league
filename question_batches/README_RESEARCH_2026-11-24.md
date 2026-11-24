# RAQTIVA Question Bank Research Log

- Workstream: source extraction and original-question authoring
- Date opened: 2026-11-24
- Standard: RAQTIVA Question Design Standard v2.3 (binding project requirement)
- Branch: question-bank/research-20261124
- Status: research in progress; nothing in this workstream is approved or published.

## Source set received

1. `نمونه سوالات استاندارد تعیین سطح مالیاتی .pdf` — 201 pages; scanned image PDF (page count verified with PDF metadata).
2. `آزمون تعیین سطح 1403 - سطح 3 - قسمت 7.pdf` — 24 pages.
3. `آزمون_مشاوران_رسمی_مالیاتی_1403_قسمت_4.pdf` — 21 pages.
4. `عمومی۱.pdf` — 8 pages; scanned image PDF.
5. `عمومی ۲.pdf` — 8 pages; scanned image PDF.

Total: 262 pages. Two 1403 PDFs expose page markers in text extraction but question bodies require image/OCR review. Three PDFs are image scans.

## Initial OCR/index observations (not a complete extraction)

Early pages expose topics including:
- reduced-development-area employment/tax relief and the location of a company's head office versus sales office;
- income tax and VAT questions;
- tax treatment of usufruct/lifetime gifts;
- VAT treatment of imported rehabilitation equipment;
- VAT period determination under Article 19;
- reassessment/limitation periods and notice deadlines;
- exchange differences for named export-support entities;
- VAT penalty base for gold, jewelry and platinum;
- VAT exemptions and dispute-resolution deadlines.

These are topic signals only. No source question text is to be copied or lightly paraphrased.

## OCR progress update (2026-11-24)

PDF metadata confirms 201 pages in the large scanned sample PDF, correcting the preliminary 150-page estimate. The full source set is therefore 262 pages.

OCR has been run on pages 1–3 of both عمومی۱.pdf and عمومی ۲.pdf. The readable topic index now additionally includes:
- 1404 employment/tax relief for staff in less-developed areas, free-trade zones, and science/technology parks;
- cigarette tax increases under the Seventh Development Plan;
- tax treatment of gratuitous residential usufruct and vacant housing;
- restrictions on departure for persons with finalized tax debts;
- tax treatment of Iranian suppliers to foreign contractors;
- FX translation differences for specified export-support institutions;
- VAT non-registration penalty base for gold/jewelry/platinum transactions;
- VAT exemptions and scope, including health, transport, insurance, print/publication, exhibition, hotel, warehousing, and immovable-property lease services;
- appeal periods and eligible appellants in tax-dispute proceedings;
- foreign-source income and private-sector employment income;
- deductible expenses attributable to exempt / zero-rated / fixed-rate income;
- VAT import territorial scope, production-unit zero-rate conditions, installment periods, export input-tax refunds, green levy commencement, and selected 1404 budget provisions.

OCR text is being used only to identify competencies and topic coverage. The scans contain recognition errors in dates, numbers, and legal references; none of those OCR fragments is treated as verified legal authority or a reliable answer key.

## Additional OCR observations

Pages 1–3 of the 1403 level-3 exam have also been OCR-reviewed. The readable items indicate competencies around:
- employment-income relief for staff at a sales office in a less-developed region when the company's head office and main residence are elsewhere;
- statutory filing duties and deadlines of the last managers of merging / consolidating companies, including supporting financial statements and valuation reporting.

Pages 1–3 of the 1403 official tax-advisers exam part 4 identify the section as “Tax Accounting and Auditing”; the sampled pages did not yet yield readable question bodies. Further page batches are required before drawing topic conclusions for this source.

## Large scanned reference PDF — initial OCR sample

OCR of the first two rendered pages of the 201-page reference PDF yielded material on inheritance tax, including:
- assets transferred by will or testamentary disposition and the distinction between heirs and non-heirs;
- inheritance-tax exemptions for heirs of martyrs;
- Article 26 inheritance-tax return deadline and required estate disclosures;
- rates for second- and third-class heirs;
- valuation date and valuation basis for estate assets and liabilities;
- liabilities arising from lease-to-own arrangements;
- valuation of vehicles, listed shares, commercial goodwill, and valuable jewelry;
- treatment of estates of persons who died before the 1395 amendments;
- deductible religious/financial obligations and funeral expenses.

The source PDF appears to be a compiled question collection: the first OCR pages include question numbers in the 40s–60s and references to multiple exam years. These findings are provisional OCR indexing only; article references, dates, amounts, and answer options must be checked against the original page image and current authoritative law before any question is drafted.

## Authoring and quality rules

- Use source exams only to identify tested competencies, topic coverage, difficulty, and exam style.
- Write independent, original fact patterns and options; do not disguise or reproduce source questions.
- Four options, exactly one defensible correct answer.
- Difficulty must be hard / very hard / specialized; exclude easy and medium questions from the published bank.
- Public answer: clear reasoning, analysis of each option, exact legal authority, article/paragraph/clause, amendment status, approval/publication dates as applicable, and authoritative source URL.
- Subscriber-only academy layer: traps, distractor construction, common errors, efficient solving sequence, time-saving tactics, and accuracy safeguards.
- Track provenance, topic, legal validity window, source verification, duplicate check, independent review, and approval state.
- Any question without fully verified legal support remains a draft and must not be published.
- Imported/official source questions are not to be republished as disguised variants.
- Paid-only material must not leak through public question or answer APIs.
- Publication requires independent review and owner approval.

## Integration gate

Before importing any batch, inspect the current question schema, serializers/API exposure, importer/validator command, and admin review workflow on the target application branch. Do not assume a command or field exists. Import only as DRAFT/PENDING_REVIEW; never publish automatically.

## Progress

- [x] Register all five source PDFs and page counts.
- [x] Create a persistent research branch and this handoff log.
- [ ] Complete page-by-page extraction/OCR and topic index.
- [ ] Verify current law and amendment history for each proposed question.
- [ ] Produce first original batch with public and subscriber layers.
- [ ] Validate against actual importer schema and duplicate checks.
- [ ] Import as drafts and verify database/API separation.
- [ ] Independent review and owner approval before publication.


## Continuation after security-review pause (2026-11-24)

The user resumed the question-bank work after submitting the separate Google Play Protect appeal. That appeal does not change the question-bank workflow.

A further OCR sample was run on pages 2–4 of `آزمون تعیین سطح 1403 - سطح 3 - قسمت 7.pdf`. The visible competencies include:
- determining the 1403 employment-income relief applicable to employees of a sales office in a less-developed area when the company's head office / principal residence is in Tehran;
- statutory post-decision reporting and disclosure duties of the last managers of merging / consolidating companies, including minutes, partner/shareholder lists, share ratios, and asset/liability statements;
- withholding obligations on payments to a foreign company resident outside Iran for services performed in Iran, where the tax-law coefficient is relevant.

This is a limited OCR sample, not a complete extraction. OCR corrupted several dates, amounts, and legal terms; the source images and applicable law must be checked before using any detail in an authored question. No answer key or legal conclusion is inferred from this sample.


## Target-branch integration reconnaissance (main, 2026-11-24)

The current `backend/apps/questions` implementation was inspected on `main` (models, serializers, views, services, admin, URLs). Findings:

- `Question` supports subjects `direct_tax`, `vat`, `taxpayer_system`, `disputes`, `audit`, and `other_laws`; provenance includes `authored`; statuses include draft, pending_review, approved, rejected, and published.
- The difficulty enum currently contains only `easy`, `medium`, and `hard`. The project's hard / very-hard / specialized taxonomy is therefore not fully represented. Do not silently map distinct levels to `hard`; assess a controlled schema change separately before importing a graded batch.
- `QuestionOption` enforces option positions 1–4. Review service checks exactly four options and exactly one correct answer; author cannot review their own question. Publishing requires prior approval by another reviewer.
- The public serializer currently exposes question id, subject, difficulty, prompt, options (without correctness), and version only. It does not expose explanation or source reference. The public list/detail views filter to published questions and require authentication.
- The inspected `backend/apps` directory has no dedicated `academy` app. No subscriber-only trap/tactic model or access-control endpoint was found in the questions app. Paid academy analysis must therefore remain out of question payloads until a separately authorized, subscription-gated design is implemented and tested.
- No importer or batch validator file was present in `backend/apps/questions` on `main`; earlier server-side tooling mentioned in project history must not be assumed to exist in this repository branch.

These are code-inspection findings, not production-server verification. No schema, API, database, deployment, or mobile files were changed. The research branch remains documentation-only.
