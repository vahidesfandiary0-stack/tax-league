from django.core.exceptions import ValidationError
from django.db import models


class AcademyContent(models.Model):
    class Category(models.TextChoices):
        FOUNDATIONS = "foundations", "مبانی تخصصی"
        TRAPOLOGY = "trapology", "تله‌شناسی"
        CASE_STUDY = "case_study", "تحلیل پرونده"
        CHECKLIST = "checklist", "چک‌لیست و مرور"

    slug = models.SlugField(max_length=160, unique=True)
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=500)
    category = models.CharField(max_length=24, choices=Category.choices)
    body = models.TextField()
    source_title = models.CharField(max_length=300)
    source_url = models.URLField(max_length=1500)
    legal_effective_date = models.DateField(null=True, blank=True)
    is_exclusive = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "-updated_at", "pk"]
        verbose_name = "محتوای آکادمی"
        verbose_name_plural = "محتواهای آکادمی"

    def clean(self):
        super().clean()
        if not self.source_title.strip() or not self.source_url.strip():
            raise ValidationError("عنوان و پیوند منبع معتبر برای محتوای آموزشی الزامی است.")
        if self.is_active and not self.body.strip():
            raise ValidationError("محتوای خالی قابل انتشار نیست.")

    def __str__(self):
        return self.title
