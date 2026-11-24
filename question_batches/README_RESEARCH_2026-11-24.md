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
