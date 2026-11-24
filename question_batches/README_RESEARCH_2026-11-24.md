# RAQTIVA Question Bank Research Log

- Workstream: source extraction and original-question authoring
- Date opened: 2026-11-24
- Standard: RAQTIVA Question Design Standard v2.3 (binding project requirement)
- Branch: question-bank/research-20261124
- Status: research in progress; nothing in this workstream is approved or published.

## Source set received

1. `نمونه سوالات استاندارد تعیین سطح مالیاتی .pdf` — 150 pages; scanned image PDF.
2. `آزمون تعیین سطح 1403 - سطح 3 - قسمت 7.pdf` — 24 pages.
3. `آزمون_مشاوران_رسمی_مالیاتی_1403_قسمت_4.pdf` — 21 pages.
4. `عمومی۱.pdf` — 8 pages; scanned image PDF.
5. `عمومی ۲.pdf` — 8 pages; scanned image PDF.

Total: 211 pages. Two 1403 PDFs expose page markers in text extraction but question bodies require image/OCR review. Three PDFs are image scans.

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
