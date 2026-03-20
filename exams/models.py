from django.db import models
from core.models import BaseModel
from departments.models import Department


class Exam(BaseModel):
    title = models.CharField(max_length=255)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='exams'
    )
    duration = models.IntegerField(help_text="Daqiqalarda (masalan: 30)")
    passing_score = models.IntegerField(
        default=35,
        help_text="O'tish uchun minimal to'g'ri javoblar soni (masalan: 35)"
    )

    def __str__(self):
        return f"{self.title} ({self.department.name})"


class Question(BaseModel):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.TextField()

    def __str__(self):
        return self.text[:80]


class Option(BaseModel):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options'
    )
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        mark = "✅" if self.is_correct else "❌"
        return f"{mark} {self.text[:50]}"
