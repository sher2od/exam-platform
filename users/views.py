from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    LoginSerializer, 
    ManagerCreateSerializer, 
    ManagerListSerializer,
    EmployeeBulkCreateSerializer,
    EmployeeListSerializer
)
from .permissions import IsAdminRole
from .models import User
from drf_spectacular.utils import extend_schema


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        tags=['Auth'],
        summary='Foydalanuvchi login (username yoki phone_number orqali)',
        request=LoginSerializer
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            # 1. Avval bloklanganligini tekshirish (test yechganlar uchun)
            u = User.objects.filter(Q(username=username) | Q(phone_number=username)).first()
            if u and not u.is_active:
                return Response(
                    {'error': 'Siz allaqachon test topshirgansiz va hisobingiz yakunlangan!'}, 
                    status=status.HTTP_403_FORBIDDEN
                )

            # 2. Keyin authenticate qilish
            user = authenticate(username=username, password=password)
            
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'role': user.role,
                    'username': user.username,
                    'phone_number': user.phone_number
                }, status=status.HTTP_200_OK)
            
            return Response({'error': 'Login yoki parol xato!'}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManagerCreateAPIView(generics.CreateAPIView):
    serializer_class = ManagerCreateSerializer
    permission_classes = [IsAdminRole]

    @extend_schema(
        tags=['Users - Manager'],
        summary='Yangi Bo\'lim boshlig\'i (Manager) yaratish (faqat ADMIN)',
        request=ManagerCreateSerializer
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ManagerListAPIView(generics.ListAPIView):
    serializer_class = ManagerListSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return User.objects.filter(role='MANAGER').select_related('department').order_by('-date_joined')

    @extend_schema(
        tags=['Users - Manager'],
        summary='Barcha Bo\'lim boshliqlarini ko\'rish (faqat ADMIN)',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ManagerDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        # Faqat role='MANAGER' bo'lganlarni topadi, boshqasini 404 qaytaradi
        return User.objects.filter(role='MANAGER')

    @extend_schema(
        tags=['Users - Manager'],
        summary='Bo\'lim boshlig\'ini o\'chirish (faqat ADMIN)',
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()  # role='MANAGER' bo'lmasa 404 qaytaradi
        instance.delete()
        return Response(
            {"message": f"'{instance.username}' muvaffaqiyatli o'chirildi."},
            status=status.HTTP_204_NO_CONTENT
        )


class EmployeeBulkCreateAPIView(APIView):
    permission_classes = [IsAdminRole]

    @extend_schema(
        tags=['Users - Employee'],
        summary='Xodimlarni Excel orqali ommaviy yaratish (faqat ADMIN)',
        request=EmployeeBulkCreateSerializer,
    )
    def post(self, request):
        serializer = EmployeeBulkCreateSerializer(data=request.data)
        if serializer.is_valid():
            created_users = serializer.save()
            # Custom representation for list
            data = serializer.to_representation(created_users)
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeListAPIView(generics.ListAPIView):
    serializer_class = EmployeeListSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        return User.objects.filter(role='EMPLOYEE').select_related('department', 'assigned_exam').order_by('-id')

    @extend_schema(
        tags=['Users - Employee'],
        summary='Barcha xodimlarni va ularga biriktirilgan testlarni ko\'rish (faqat ADMIN)',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EmployeeDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        # Faqat role='EMPLOYEE' bo'lgan xodimlarni topadi
        return User.objects.filter(role='EMPLOYEE')

    @extend_schema(
        tags=['Users - Employee'],
        summary='Xodimni butunlay o\'chirish (faqat ADMIN)',
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": f"Xodim '{instance.username}' muvaffaqiyatli o'chirildi."},
            status=status.HTTP_204_NO_CONTENT
        )
