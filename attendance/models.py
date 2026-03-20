from django.db import models
from django.conf import settings
from exams.models import Exam

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('KUTILMOQDA', 'KUTILMOQDA'),
        ('JARAYONDA', 'JARAYONDA'),
        ('TUGATDI', 'TUGATDI'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendances')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='KUTILMOQDA')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exam.title} ({self.status})"
