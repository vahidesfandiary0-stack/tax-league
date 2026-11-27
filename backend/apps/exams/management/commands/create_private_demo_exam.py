from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.accounts.models import User
from apps.exams.models import Exam, ExamQuestion
from apps.exams.services import publish_exam
from apps.questions.models import Question, QuestionOption


DEMO_ITEMS = [
    (
        "کدام مورد، مالیات مستقیم محسوب می‌شود؟",
        ["مالیات بر درآمد", "عوارض شهرداری", "حقوق گمرکی", "مالیات بر ارزش افزوده"],
        0,
        "مالیات بر درآمد از مصادیق مالیات‌های مستقیم است.",
    ),
    (
        "در مالیات بر ارزش افزوده، مؤدی در حالت معمول مالیات دریافتی از خریدار را چگونه گزارش می‌کند؟",
        ["به‌عنوان مالیات و عوارض فروش", "به‌عنوان هزینه حقوق", "به‌عنوان درآمد معاف", "به‌عنوان مالیات حقوق کارکنان"],
        0,
        "مالیات و عوارض فروش در محاسبه بدهی دوره با اعتبار مالیاتی خرید سنجیده می‌شود.",
    ),
    (
        "کدام گزینه نمونه‌ای از اطلاعات هویتی مؤدی در پرونده مالیاتی است؟",
        ["شناسه ملی یا شماره ملی", "رنگ سربرگ فاکتور", "نام نرم‌افزار حسابداری", "شماره سریال رایانه"],
        0,
        "شناسه ملی اشخاص حقوقی و شماره ملی اشخاص حقیقی از شناسه‌های هویتی‌اند.",
    ),
    (
        "هدف اصلی نگهداری اسناد و مدارک هزینه چیست؟",
        ["اثبات وقوع و ارتباط هزینه با فعالیت", "افزایش خودکار نرخ مالیات", "حذف تکلیف اظهارنامه", "جایگزینی دفاتر با تبلیغات"],
        0,
        "اسناد معتبر برای احراز وقوع، مبلغ و ارتباط هزینه با فعالیت اهمیت دارند.",
    ),
    (
        "در رسیدگی مالیاتی، کدام رویکرد حرفه‌ای مناسب‌تر است؟",
        ["استناد به قانون و مدارک قابل اتکا", "اتکا به شنیده‌های غیرمستند", "نادیده گرفتن تاریخ اسناد", "انتخاب پاسخ بر اساس حدس"],
        0,
        "نتیجه رسیدگی باید بر مستندات و مقررات معتبر استوار باشد.",
    ),
]


class Command(BaseCommand):
    help = "Create a public, non-league demo exam for all authenticated users."

    @transaction.atomic
    def handle(self, *args, **options):
        author = User.objects.filter(is_active=True, is_staff=True).order_by("pk").first()
        if author is None:
            author = User.objects.filter(is_active=True).order_by("pk").first()
        if author is None:
            raise CommandError("برای ثبت سؤالات آزمون، هیچ کاربر فعالی وجود ندارد.")

        title = "آزمون آزمایشی عمومی RAQTIVA"
        exam, created = Exam.objects.get_or_create(
            title=title,
            test_user=None,
            defaults={
                "kind": Exam.Kind.MOCK,
                "description": "آزمون عمومی و موقت برای بررسی شروع، پاسخ‌گویی، ثبت نتیجه و نمایش سوابق؛ فاقد اثر بر رتبه‌بندی لیگ.",
                "duration_minutes": 10,
                "max_attempts": 20,
                "counts_for_league": False,
                "requires_purchase": False,
                "status": Exam.Status.DRAFT,
            },
        )
        if not created and exam.status == Exam.Status.PUBLISHED:
            self.stdout.write(self.style.SUCCESS(f"آزمون آزمایشی عمومی از قبل فعال است: {exam.pk}"))
            return
        if not created and exam.status != Exam.Status.DRAFT:
            raise CommandError("آزمون موجود در وضعیت قابل انتشار نیست.")

        for index, (prompt, choices, correct, explanation) in enumerate(DEMO_ITEMS, start=1):
            question = Question.objects.create(
                subject=Question.Subject.DIRECT_TAX,
                difficulty=Question.Difficulty.EASY,
                prompt=prompt,
                explanation=explanation,
                provenance=Question.Provenance.AUTHORED,
                provenance_note="محتوای ساده و صرفاً آزمایشی؛ غیرقابل استفاده در آزمون رسمی شبانه.",
                status=Question.Status.PUBLISHED,
                author=author,
            )
            for position, choice in enumerate(choices, start=1):
                QuestionOption.objects.create(
                    question=question,
                    position=position,
                    text=choice,
                    is_correct=(position - 1 == correct),
                )
            ExamQuestion.objects.create(
                exam=exam,
                question=question,
                position=index,
                points_correct=10,
                points_wrong=0,
            )

        publish_exam(exam.pk)
        self.stdout.write(self.style.SUCCESS(
            f"آزمون آزمایشی عمومی با {len(DEMO_ITEMS)} سؤال منتشر شد. شناسه آزمون: {exam.pk}"
        ))
