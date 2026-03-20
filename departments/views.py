from rest_framework import viewsets, mixins, permissions, status
from rest_framework.response import Response
from .models import Department
from .serializers import DepartmentSerializer
from drf_spectacular.utils import extend_schema

class IsAdminForModify(permissions.BasePermission):
    """
    Ko'rish uchun IsAuthenticated, 
    Yaratish va O'chirish (Create/Destroy) uchun esa faqat ADMIN ruxsati.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
            
        # SAFE_METHODS: GET (list, retrieve), HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # POST (create) va DELETE (destroy) uchun role='ADMIN' tekshiruvi
        return request.user.role == 'ADMIN'

class DepartmentViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """
    Departmentlar uchun API: 
    - List/Retrieve (Hamma userlar uchun)
    - Create/Destroy (Faqat ADMIN uchun)
    - Update/Partial Update BUTUNLAY BLOKLANGAN (Bloklangan mixin'lar tufayli)
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminForModify]

    @extend_schema(tags=['Departments'], summary='Barcha bo\'limlar ro\'yxati')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=['Departments'], summary='Yangi bo\'lim yaratish (faqat ADMIN)')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(tags=['Departments'], summary='Bitta bo\'lim ma\'lumotini ko\'rish')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(tags=['Departments'], summary='Bo\'limni o\'chirish (faqat ADMIN va bo\'sh bo\'lim)')
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Bo'limda xodimlar bor-yo'qligini tekshirish
        if instance.users.exists():
            return Response(
                {"error": "Bu bo'limda xodimlar bor, uni o'chirish taqiqlanadi!"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        self.perform_destroy(instance)
        return Response(
            {"message": "Bo'lim muvaffaqiyatli o'chirildi."}, 
            status=status.HTTP_204_NO_CONTENT
        )
