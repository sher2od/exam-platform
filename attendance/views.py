from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Attendance
from .serializers import AttendanceSerializer
from users.permissions import IsAdminRole
from exams.models import Exam

class CheckInAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceSerializer

    @extend_schema(
        tags=['Attendance'],
        summary='Xodim testni boshlashdan oldin "Check-in" qilishi uchun',
    )
    def post(self, request, *args, **kwargs):
        # 1. IP va User-Agent ma'lumotlarini olish
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if not ip:
            ip = request.META.get('REMOTE_ADDR')
        
        device = request.META.get('HTTP_USER_AGENT', 'Noma\'lum qurilma')[:255]

        # 2. Xodimga biriktirilgan testni olish (faqat assigned_exam dagi testni boshlay oladi)
        assigned_exam = request.user.assigned_exam
        if not assigned_exam:
            return Response(
                {"error": "Sizga hech qanday test biriktirilmagan!"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Attendance yaratish yoki mavjudini yangilash
        attendance, created = Attendance.objects.update_or_create(
            user=request.user,
            exam=assigned_exam,
            defaults={
                'status': 'JARAYONDA',
                'ip_address': ip,
                'device_info': device
            }
        )

        serializer = self.get_serializer(attendance)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class AttendanceListAPIView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Attendance'],
        summary='Barcha xodimlar davomatini ko\'rish (Admin/Manager)',
    )
    def get(self, request, *args, **kwargs):
        # Manager o'z bo'limiga tegishli testlardagi davomatni ko'radi
        if request.user.role == 'EMPLOYEE':
            return Response(
                {"error": "Bu ro'yxatni ko'rishga ruxsatingiz yo'q!"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Attendance.objects.all().order_by('-created_at')
        
        if user.role == 'MANAGER':
            return Attendance.objects.filter(
                exam__department=user.department
            ).order_by('-created_at')
        
        return Attendance.objects.none()
