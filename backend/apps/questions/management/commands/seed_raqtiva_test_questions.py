from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.questions.models import Question, QuestionOption


TEST_PREFIX = "[RAQTIVA-TEST-ONLY] "


QUESTIONS = [
    {
        "subject": Question.Subject.DIRECT_TAX,
        "difficulty": Question.Difficulty.VERY_HARD,
        "prompt": TEST_PREFIX + "شرکت الف در سال مالی مبلغ ۸ میلیارد ریال هزینه در دفاتر ثبت کرده است. در رسیدگی مشخص می‌شود ۱٫۲ میلیارد ریال از هزینه‌ها فاقد مدارک کافی برای احراز ارتباط با فعالیت شرکت است؛ شرکت ادعا می‌کند تمام مبلغ واقعاً پرداخت شده است. کدام تحلیل دقیق‌تر است؟",
        "explanation": "پاسخ تشریحی عمومیِ آزمایشی: پاسخ صحیح گزینه سوم است؛ این نمونه صرفاً برای بررسی گردش کار فنی ساخته شده و استناد حقوقی معتبر ندارد.",
        "source_reference": "صرفاً داده آزمایشی؛ فاقد استناد قانونی و غیرقابل انتشار رسمی.",
        "options": [
            ("صرف پرداخت واقعی برای پذیرش مالیاتی هزینه کافی است.", False),
            ("تمام هزینه‌ها باید پذیرفته شوند، مگر آنکه صوری بودن آن‌ها اثبات شود.", False),
            ("پرداخت واقعی به‌تنهایی کافی نیست و قابلیت قبول مالیاتی هزینه باید با شرایط قانونی و مستندات مربوط احراز شود.", True),
            ("هزینه فاقد فاکتور معتبر در همه شرایط باید به‌عنوان درآمد اتفاقی شرکت تلقی شود.", False),
        ],
    },
    {
        "subject": Question.Subject.VAT,
        "difficulty": Question.Difficulty.VERY_HARD,
        "prompt": TEST_PREFIX + "یک مؤدی در اظهارنامه مالیات بر ارزش افزوده، اعتبار مالیاتی خریدی را مطالبه کرده است. صورتحساب در سامانه ثبت شده، اما اطلاعات معامله با اسناد حمل و موجودی انبار تطبیق ندارد. کدام اقدام از نظر رسیدگی دقیق‌تر است؟",
        "explanation": "پاسخ تشریحی عمومیِ آزمایشی: پاسخ صحیح گزینه سوم است؛ این نمونه صرفاً برای بررسی گردش کار فنی ساخته شده و استناد حقوقی معتبر ندارد.",
        "source_reference": "صرفاً داده آزمایشی؛ فاقد استناد قانونی و غیرقابل انتشار رسمی.",
        "options": [
            ("پذیرش قطعی اعتبار، چون صورتحساب در سامانه ثبت شده است.", False),
            ("رد قطعی اعتبار، صرفاً به دلیل وجود مغایرت در اسناد حمل.", False),
            ("بررسی واقعی بودن معامله، ارتباط خرید با فعالیت اقتصادی، اسناد پشتیبان و شرایط قانونی پذیرش اعتبار پیش از تصمیم‌گیری.", True),
            ("پذیرش اعتبار، مشروط به اینکه فروشنده اظهارنامه خود را تسلیم کرده باشد.", False),
        ],
    },
]


class Command(BaseCommand):
    help = "Create two private, unpublished RAQTIVA test questions (DEBUG environments only)."

    def add_arguments(self, parser):
        parser.add_argument("--author-id", type=int, required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("این داده‌ها فقط در محیط آزمایشی با DEBUG=True قابل ایجاد هستند.")
        User = get_user_model()
        author = User.objects.filter(pk=options["author_id"], is_superuser=True).first()
        if author is None:
            raise CommandError("--author-id باید شناسه یک مدیر ارشد موجود باشد.")

        created_count = 0
        for item in QUESTIONS:
            prompt = item["prompt"]
            existing = Question.objects.filter(prompt=prompt).first()
            if existing:
                if existing.status != Question.Status.DRAFT or existing.author_id != author.pk:
                    raise CommandError("نمونه‌ای با همین متن وجود دارد اما پیش‌نویس آزمایشی متعلق به این مدیر نیست.")
                self.stdout.write(f"از قبل موجود است: {existing.pk}")
                continue

            question = Question.objects.create(
                subject=item["subject"],
                difficulty=item["difficulty"],
                prompt=prompt,
                explanation=item["explanation"],
                source_reference=item["source_reference"],
                provenance=Question.Provenance.AUTHORED,
                provenance_note="TEST ONLY — do not publish; no verified legal citation.",
                status=Question.Status.DRAFT,
                author=author,
            )
            QuestionOption.objects.bulk_create([
                QuestionOption(question=question, position=index, text=text, is_correct=is_correct)
                for index, (text, is_correct) in enumerate(item["options"], start=1)
            ])
            created_count += 1
            self.stdout.write(f"پیش‌نویس آزمایشی ایجاد شد: {question.pk}")

        self.stdout.write(self.style.SUCCESS(f"تعداد پیش‌نویس‌های جدید: {created_count}. هیچ سؤالی منتشر نشد."))
