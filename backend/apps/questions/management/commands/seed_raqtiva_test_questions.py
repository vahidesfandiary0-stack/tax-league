from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.questions.models import Question, QuestionOption


QUESTIONS = [
    {
        "subject": Question.Subject.VAT,
        "difficulty": Question.Difficulty.VERY_HARD,
        "prompt": "شرکت «الف» که تولیدکننده تجهیزات صنعتی است، یک دستگاه مشمول مالیات بر ارزش افزوده را با خدمات تعمیرات اساسی خطوط تولید شرکت «ب» معاوضه می‌کند. ارزش توافق‌شده دو عوض برابر است؛ هیچ وجه نقدی ردوبدل نمی‌شود و هر دو طرف، مؤدی مشمول این قانون‌اند. شرکت «الف» استدلال می‌کند چون وجهی دریافت نکرده، عرضه‌ای از نظر مالیات بر ارزش افزوده انجام نداده است. کدام تحلیل با حکم قانون سازگار است؟",
        "explanation": "پاسخ صحیح گزینه ۳ است. مطابق تبصره ۲ ماده ۲ قانون مالیات بر ارزش افزوده مصوب ۱۴۰۰، در معاوضه کالا و خدمات، عرضه کالا و ارائه خدمت از طرف هر یک از متعاملین تحقق‌یافته محسوب می‌شود و هر طرف باید حکم مالیاتی مربوط به عرضه خود را رعایت کند. نبود وجه نقد یا برابری ارزش دو عوض، به‌تنهایی موجب خروج معامله از شمول قانون نیست. این حکم به معنای نادیده گرفتن معافیت‌های قانونی احتمالی هر عرضه نیست؛ در فرض سؤال، هر دو عرضه مشمول فرض شده‌اند.",
        "source_reference": "قانون مالیات بر ارزش افزوده مصوب ۱۴۰۰، ماده ۲، تبصره ۲؛ متن قانون: https://dadyar.org/library/laws/value-added-tax-law-1400",
        "options": [
            ("فقط شرکت «ب» عرضه خدمت انجام داده است؛ بنابراین صرفاً شرکت «ب» باید آثار مالیات بر ارزش افزوده را بررسی کند.", False),
            ("چون ارزش دو عوض برابر است و وجه نقدی مبادله نشده، هیچ‌یک از طرفین عرضه مشمولی انجام نداده‌اند.", False),
            ("هر یک از دو شرکت از بابت عرضه‌ای که انجام داده، عرضه‌کننده محسوب می‌شود و باید مقررات مالیات بر ارزش افزوده را درباره عرضه خود رعایت کند.", True),
            ("فقط شرکتی که در قرارداد، کالا را واگذار کرده است عرضه‌کننده محسوب می‌شود؛ ارائه خدمت در معاوضه، عرضه مستقل نیست.", False),
        ],
    },
    {
        "subject": Question.Subject.VAT,
        "difficulty": Question.Difficulty.VERY_HARD,
        "prompt": "شرکت «الف» در ۱۵ مهر، کالای مشمول مالیات را به‌صورت شش‌ماهه و اقساطی به شرکت «ب» می‌فروشد و صورتحساب الکترونیکی را همان روز صادر می‌کند. قرارداد نسیه و برنامه دریافت اقساط در سامانه مؤدیان ثبت و به تأیید طرفین رسیده است. نخستین قسط در ۱۵ آبان پرداخت می‌شود. با فرض رعایت سایر شرایط قانونی، کدام گزینه درباره زمان تعلق مالیات، تأخیر در پرداخت آن و اعتبار مالیاتی خریدار صحیح است؟",
        "explanation": "پاسخ صحیح گزینه ۲ است. بر اساس ماده ۳ قانون مالیات بر ارزش افزوده، تاریخ تعلق مالیات و عوارض اصولاً تاریخ صدور صورتحساب است. مطابق تبصره‌های ۱ و ۲ ماده ۴، ثبت معامله غیرنقدی و دریافت‌وپرداخت‌های مرتبط و تأیید طرفین در سامانه مؤدیان شرط برخورداری از حکم معامله غیرنقدی است؛ در این صورت فروشنده می‌تواند پرداخت مالیات و عوارض فروش را متناسب با دریافت ثمن، تا زمان دریافت اقساط به تأخیر بیندازد و تا آن زمان مشمول جریمه تأخیر بابت مبلغ پرداخت‌نشده نمی‌شود. همچنین تا پرداخت مالیات و عوارض توسط خریدار، اعتبار مالیاتی مربوط برای او منظور نمی‌شود. بنابراین باید میان تاریخ تعلق مالیات و زمان مجاز پرداخت آن تفکیک کرد.",
        "source_reference": "قانون مالیات بر ارزش افزوده مصوب ۱۴۰۰، ماده ۳ و تبصره‌های ۱ و ۲ ماده ۴؛ متن قانون: https://dadyar.org/library/laws/value-added-tax-law-1400",
        "options": [
            ("مالیات فقط در تاریخ دریافت آخرین قسط تعلق می‌گیرد و خریدار از تاریخ صدور صورتحساب حق اعتبار مالیاتی دارد.", False),
            ("تاریخ تعلق مالیات، تاریخ صدور صورتحساب است؛ فروشنده با رعایت شرط ثبت و تأیید معامله در سامانه می‌تواند پرداخت را متناسب با وصول اقساط به تأخیر اندازد و اعتبار مالیاتی خریدار نیز تا پرداخت مالیات منظور نمی‌شود.", True),
            ("تاریخ تعلق مالیات، تاریخ صدور صورتحساب است و فروشنده در هیچ شرایطی حق تأخیر متناسب در پرداخت مالیات فروش را ندارد.", False),
            ("ثبت معامله در سامانه فقط برای اثبات قرارداد است؛ حتی با تأیید طرفین، معامله از نظر مالیات نقدی محسوب می‌شود و خریدار فوراً اعتبار مالیاتی می‌گیرد.", False),
        ],
    },
]


class Command(BaseCommand):
    help = "Create two source-cited VAT questions as unpublished drafts for owner review."

    def add_arguments(self, parser):
        parser.add_argument("--author-id", type=int, required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("این دستور فقط در محیط DEBUG قابل اجراست؛ برای ثبت در پایگاه داده عملیاتی از مسیر انتشار مدیریتی استفاده کنید.")
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
                    raise CommandError("سؤالی با همین متن وجود دارد اما پیش‌نویس متعلق به این مدیر نیست؛ هیچ رکوردی تغییر نکرد.")
                self.stdout.write(f"از قبل موجود است: {existing.pk}")
                continue

            question = Question.objects.create(
                subject=item["subject"],
                difficulty=item["difficulty"],
                prompt=prompt,
                explanation=item["explanation"],
                source_reference=item["source_reference"],
                provenance=Question.Provenance.AUTHORED,
                provenance_note="تألیف مستقل بر پایه قانون مالیات بر ارزش افزوده مصوب ۱۴۰۰؛ نیازمند تأیید نهایی مالک پیش از انتشار.",
                status=Question.Status.DRAFT,
                author=author,
            )
            QuestionOption.objects.bulk_create([
                QuestionOption(question=question, position=index, text=text, is_correct=is_correct)
                for index, (text, is_correct) in enumerate(item["options"], start=1)
            ])
            created_count += 1
            self.stdout.write(f"پیش‌نویس مستند ایجاد شد: {question.pk}")

        self.stdout.write(self.style.SUCCESS(f"تعداد پیش‌نویس‌های جدید: {created_count}. هیچ سؤالی منتشر نشد."))
