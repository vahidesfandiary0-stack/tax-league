import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.dateparse import parse_date

from apps.questions.models import Question, QuestionOption


ALLOWED_SUBJECTS = {choice[0] for choice in Question.Subject.choices}
ALLOWED_DIFFICULTIES = {
    Question.Difficulty.HARD,
    Question.Difficulty.VERY_HARD,
    Question.Difficulty.SPECIALIZED,
}


class Command(BaseCommand):
    help = "Validate a JSON batch and optionally import questions as DRAFT only."

    def add_arguments(self, parser):
        parser.add_argument("file", type=Path)
        parser.add_argument("--author-id", type=int, required=True)
        parser.add_argument("--commit", action="store_true", help="Persist validated questions as DRAFT.")

    def handle(self, *args, **options):
        path = options["file"]
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError(f"Cannot read valid UTF-8 JSON: {exc}") from exc

        if not isinstance(payload, list) or not payload:
            raise CommandError("Batch must be a non-empty JSON array.")

        author = get_user_model().objects.filter(pk=options["author_id"], is_active=True).first()
        if author is None:
            raise CommandError("Active author account not found.")

        normalized_prompts = set()
        validated = []
        errors = []
        for index, item in enumerate(payload, start=1):
            try:
                if not isinstance(item, dict):
                    raise ValueError("each item must be an object")
                subject = item.get("subject")
                difficulty = item.get("difficulty")
                prompt = item.get("prompt")
                explanation = item.get("explanation")
                source = item.get("source_reference")
                valid_from = parse_date(item.get("valid_from", ""))
                options_list = item.get("options")

                if subject not in ALLOWED_SUBJECTS:
                    raise ValueError("invalid subject")
                if difficulty not in ALLOWED_DIFFICULTIES:
                    raise ValueError("night-bank questions must be hard, very_hard, or specialized")
                if not isinstance(prompt, str) or len(prompt.strip()) < 30:
                    raise ValueError("prompt must contain at least 30 characters")
                if not isinstance(explanation, str) or len(explanation.strip()) < 30:
                    raise ValueError("explanation must contain at least 30 characters")
                if not isinstance(source, str) or not source.strip():
                    raise ValueError("source_reference is required")
                if valid_from is None:
                    raise ValueError("valid_from must be an ISO date (YYYY-MM-DD)")
                if not isinstance(options_list, list) or len(options_list) != 4:
                    raise ValueError("exactly four options are required")
                if any(not isinstance(opt, dict) or not isinstance(opt.get("text"), str) or not opt["text"].strip() for opt in options_list):
                    raise ValueError("each option must have non-empty text")
                if sum(opt.get("is_correct") is True for opt in options_list) != 1:
                    raise ValueError("exactly one option must be marked is_correct=true")

                key = " ".join(prompt.casefold().split())
                if key in normalized_prompts or Question.objects.filter(prompt__iexact=prompt.strip()).exists():
                    raise ValueError("duplicate prompt in batch or existing bank")
                normalized_prompts.add(key)
                validated.append((item, valid_from))
            except (TypeError, ValueError) as exc:
                errors.append(f"item {index}: {exc}")

        if errors:
            raise CommandError("Batch rejected; no rows written:\\n" + "\\n".join(errors))

        self.stdout.write(self.style.SUCCESS(f"VALID: {len(validated)} questions; all will remain DRAFT."))
        if not options["commit"]:
            self.stdout.write("Preview only. Add --commit to persist.")
            return

        with transaction.atomic():
            for item, valid_from in validated:
                question = Question.objects.create(
                    subject=item["subject"],
                    difficulty=item["difficulty"],
                    prompt=item["prompt"].strip(),
                    explanation=item["explanation"].strip(),
                    source_reference=item["source_reference"].strip(),
                    valid_from=valid_from,
                    valid_until=parse_date(item.get("valid_until", "")),
                    provenance=Question.Provenance.AUTHORED,
                    provenance_note=(item.get("provenance_note") or "").strip()[:500],
                    status=Question.Status.DRAFT,
                    author=author,
                )
                QuestionOption.objects.bulk_create([
                    QuestionOption(
                        question=question,
                        position=position,
                        text=option["text"].strip(),
                        is_correct=option["is_correct"] is True,
                    )
                    for position, option in enumerate(item["options"], start=1)
                ])
        self.stdout.write(self.style.SUCCESS(f"IMPORTED: {len(validated)} DRAFT questions. Nothing was published."))
