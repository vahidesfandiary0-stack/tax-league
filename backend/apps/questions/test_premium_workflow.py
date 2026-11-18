import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.questions.models import Question, QuestionPremiumLesson
from apps.questions.services import (
    publish_premium_lesson,
    review_premium_lesson,
    submit_premium_lesson_for_review,
)


def make_lesson():
    User = get_user_model()
    author = User.objects.create_user(phone_number="09125550001")
    reviewer = User.objects.create_user(phone_number="09125550002")
    question = Question.objects.create(
        subject=Question.Subject.DIRECT_TAX,
        prompt="سؤال آزمایشی",
        author=author,
    )
    lesson = QuestionPremiumLesson.objects.create(
        question=question,
        author=author,
        traps_and_techniques="تله",
        trap_detection_signals="نشانه",
        distractor_analysis="تحلیل گزینه",
        fast_solving_method="روش حل",
        setter_insight="بینش طراح",
        common_mistakes="خطای رایج",
        supplementary_practice="تمرین",
    )
    return lesson, author, reviewer


@pytest.mark.django_db
def test_premium_lesson_requires_author_submission_and_independent_review():
    lesson, author, reviewer = make_lesson()
    with pytest.raises(ValidationError):
        submit_premium_lesson_for_review(lesson.pk, reviewer)
    submitted = submit_premium_lesson_for_review(lesson.pk, author)
    assert submitted.status == QuestionPremiumLesson.Status.REVIEW
    with pytest.raises(ValidationError):
        review_premium_lesson(lesson.pk, author, approve=True)
    approved = review_premium_lesson(lesson.pk, reviewer, approve=True)
    assert approved.status == QuestionPremiumLesson.Status.APPROVED
    assert approved.reviewer_id == reviewer.pk
    assert approved.reviewed_at is not None


@pytest.mark.django_db
def test_premium_lesson_cannot_publish_without_approval_or_reviewer():
    lesson, author, reviewer = make_lesson()
    with pytest.raises(ValidationError):
        publish_premium_lesson(lesson.pk)
    submit_premium_lesson_for_review(lesson.pk, author)
    with pytest.raises(ValidationError):
        publish_premium_lesson(lesson.pk)
    review_premium_lesson(lesson.pk, reviewer, approve=True)
    published = publish_premium_lesson(lesson.pk)
    assert published.status == QuestionPremiumLesson.Status.PUBLISHED
    assert published.published_at is not None


@pytest.mark.django_db
def test_model_save_cannot_bypass_workflow_or_edit_published_lesson():
    lesson, author, reviewer = make_lesson()
    lesson.status = QuestionPremiumLesson.Status.PUBLISHED
    with pytest.raises(ValidationError):
        lesson.save()
    lesson.refresh_from_db()
    submit_premium_lesson_for_review(lesson.pk, author)
    review_premium_lesson(lesson.pk, reviewer, approve=True)
    publish_premium_lesson(lesson.pk)
    lesson.refresh_from_db()
    lesson.traps_and_techniques = "تغییر غیرمجاز"
    with pytest.raises(ValidationError):
        lesson.save()


@pytest.mark.django_db
def test_review_rejection_returns_lesson_to_draft_for_correction():
    lesson, author, reviewer = make_lesson()
    submit_premium_lesson_for_review(lesson.pk, author)
    rejected = review_premium_lesson(lesson.pk, reviewer, approve=False)
    assert rejected.status == QuestionPremiumLesson.Status.DRAFT
    assert rejected.reviewer_id == reviewer.pk
    assert rejected.reviewed_at is not None



@pytest.mark.django_db
def test_lesson_content_is_locked_while_waiting_for_review():
    lesson, author, reviewer = make_lesson()
    submit_premium_lesson_for_review(lesson.pk, author)
    lesson.refresh_from_db()
    lesson.traps_and_techniques = "تغییر بعد از ارسال"
    with pytest.raises(ValidationError):
        lesson.save()


@pytest.mark.django_db
def test_incomplete_premium_lesson_cannot_be_approved():
    lesson, author, reviewer = make_lesson()
    lesson.supplementary_practice = ""
    lesson.save(update_fields=["supplementary_practice"])
    submit_premium_lesson_for_review(lesson.pk, author)
    with pytest.raises(ValidationError):
        review_premium_lesson(lesson.pk, reviewer, approve=True)
