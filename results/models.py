from django.db import models
from django.conf import settings
from core.models import BaseModel
from exams.models import Exam


class Attempt(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    skipped_questions = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    is_passed = models.BooleanField(default=False)

    def __str__(self):
        status = "✅ O'tdi" if self.is_passed else "❌ O'tmadi"
        return f"{self.user} - {self.exam.title} ({status})"
