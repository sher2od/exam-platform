from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Attempt
from .serializers import (
    StartExamSerializer, 
    SubmitExamSerializer, 
    AttemptResultSerializer,
    AttemptListSerializer
)
from exams.models import Exam, Option
from drf_spectacular.utils import extend_schema


class StartExamAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StartExamSerializer

    @extend_schema(
        tags=['Results'],
        summary='Testni boshlash (Attempt yaratish)',
        request=StartExamSerializer,
    )
    def post(self, request):
        serializer = StartExamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        exam_id = serializer.validated_data['exam_id']

        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return Response(
                {"error": "Test topilmadi!"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Tugallanmagan urinish bor-yo'qligini tekshirish
        existing = Attempt.objects.filter(
            user=request.user, exam=exam, end_time__isnull=True
        ).first()

        if existing:
            return Response({
                "message": "Sizda davom etayotgan urinish bor!",
                "attempt_id": existing.id,
                "exam_title": exam.title,
                "duration": exam.duration,
                "start_time": existing.start_time,
            }, status=status.HTTP_200_OK)

        # Yangi urinish yaratish
        total_q = exam.questions.count()
        attempt = Attempt.objects.create(
            user=request.user,
            exam=exam,
            total_questions=total_q,
        )

        return Response({
            "message": "Test boshlandi!",
            "attempt_id": attempt.id,
            "exam_title": exam.title,
            "duration": exam.duration,
            "total_questions": total_q,
            "start_time": attempt.start_time,
        }, status=status.HTTP_201_CREATED)


class SubmitExamAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubmitExamSerializer

    @extend_schema(
        tags=['Results'],
        summary='Test javoblarini yuborish va natijani hisoblash',
        request=SubmitExamSerializer,
    )
    def post(self, request):
        serializer = SubmitExamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        attempt_id = serializer.validated_data['attempt_id']
        answers = serializer.validated_data['answers']

        # 1. Urinishni topish
        try:
            attempt = Attempt.objects.select_related('exam').get(
                id=attempt_id, user=request.user
            )
        except Attempt.DoesNotExist:
            return Response(
                {"error": "Urinish topilmadi!"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Allaqachon topshirilganmi?
        if attempt.end_time is not None:
            return Response(
                {"error": "Bu test allaqachon topshirilgan!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        exam = attempt.exam
        now = timezone.now()
        deadline = attempt.start_time + timedelta(minutes=exam.duration)
        is_timeout = now > deadline

        # 3. Javoblarni tekshirish (vaqt tugasa ham chala javoblarni qabul qiladi)
        correct = 0
        for answer in answers:
            try:
                option = Option.objects.get(
                    id=answer['option_id'],
                    question_id=answer['question_id']
                )
                if option.is_correct:
                    correct += 1
            except Option.DoesNotExist:
                pass

        # 4. Hisoblash
        total = attempt.total_questions
        wrong = total - correct  # Yechilmagan + noto'g'ri = jami - to'g'ri
        is_passed = correct >= exam.passing_score

        # 5. Natijani saqlash
        attempt.end_time = now
        attempt.correct_answers = correct
        attempt.wrong_answers = wrong
        attempt.is_passed = is_passed
        attempt.save()

        # 6. Testdan so'ng xodimni bloklash (faqat xodim bo'lsa)
        user = request.user
        if user.role == 'EMPLOYEE':
            user.is_active = False
            user.save()

        message = "Vaqt tugadi! Chala javoblar baholandi." if is_timeout else "Test yakunlandi!"

        return Response({
            "message": message,
            "total_questions": total,
            "correct_answers": correct,
            "wrong_answers": wrong,
            "passing_score": exam.passing_score,
            "is_passed": is_passed,
        }, status=status.HTTP_200_OK)


class ResultListAPIView(generics.ListAPIView):
    serializer_class = AttemptListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'ADMIN':
            return Attempt.objects.all().select_related('user', 'exam', 'exam__department').order_by('-start_time')
        
        if user.role == 'MANAGER':
            return Attempt.objects.filter(
                exam__department=user.department
            ).select_related('user', 'exam', 'exam__department').order_by('-start_time')
        
        # Xodimlar uchun bo'sh ro'yxat (yoki 403)
        return Attempt.objects.none()

    @extend_schema(
        tags=['Results'],
        summary='Barcha test natijalarini ko\'rish (Admin/Manager)',
    )
    def get(self, request, *args, **kwargs):
        if request.user.role == 'EMPLOYEE':
            return Response(
                {'error': 'Xodimlar natijalar ro\'yxatini ko\'ra olmaydi!'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().get(request, *args, **kwargs)

