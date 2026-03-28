from django.db import models
from django.conf import settings
from core.models import BaseModel
from exams.models import Exam, Question, Option


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


class UserAnswer(BaseModel):
    attempt = models.ForeignKey(
        Attempt,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='user_answers'
    )
    selected_option = models.ForeignKey(
        Option,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_selections'
    )
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.attempt.user} - {self.question.text[:30]}"
