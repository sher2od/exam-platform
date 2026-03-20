from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Exam, Question
from .serializers import ExamCreateSerializer, ExamListSerializer, QuestionEmployeeSerializer
from users.permissions import IsAdminRole
from drf_spectacular.utils import extend_schema


class ExamCreateAPIView(generics.CreateAPIView):
    serializer_class = ExamCreateSerializer
    permission_classes = [IsAdminRole]

    @extend_schema(
        tags=['Exams'],
        summary='Yangi test yaratish (Excel yuklash, faqat ADMIN)',
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ExamListAPIView(generics.ListAPIView):
    serializer_class = ExamListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Exam.objects.select_related('department').prefetch_related('questions').all()

    @extend_schema(
        tags=['Exams'],
        summary='Barcha testlar ro\'yxati',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ExamDeleteAPIView(generics.DestroyAPIView):
    queryset = Exam.objects.all()
    permission_classes = [IsAuthenticated, IsAdminRole]

    @extend_schema(
        tags=['Exams'],
        summary='Testni o\'chirish (Savol va variantlari bilan, faqat ADMIN)',
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class EmployeeExamQuestionsAPIView(generics.ListAPIView):
    serializer_class = QuestionEmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Foydalanuvchiga biriktirilgan testni olish
        assigned_exam = self.request.user.assigned_exam
        
        if assigned_exam:
            # Faqat shu testga tegishli savollarni qaytarish
            return Question.objects.filter(exam=assigned_exam)
        
        return Question.objects.none()

    @extend_schema(
        tags=['Exams'],
        summary='Xodimga biriktirilgan test savollarini olish (Anti-cheat)',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
