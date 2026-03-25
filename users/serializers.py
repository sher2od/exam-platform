import random
import openpyxl
from io import BytesIO
from rest_framework import serializers
from django.db.models import Q
from .models import User
from drf_spectacular.utils import extend_schema_field
from departments.models import Department
from exams.models import Exam

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="Username yoki telefon raqami")
    password = serializers.CharField(write_only=True)

class ManagerCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        help_text="Bo'lim ID'si"
    )

    class Meta:
        model = User
        fields = ['username', 'phone_number', 'first_name', 'last_name', 'department_id', 'description']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'description': {'required': False},
        }

    def validate(self, attrs):
        username = attrs.get('username') or None
        phone_number = attrs.get('phone_number') or None

        # 1. Kamida bittasi kiritilishi shart
        if not username and not phone_number:
            raise serializers.ValidationError(
                {"error": "username yoki phone_number dan kamida bittasi kiritilishi shart!"}
            )

        # 2. Bo'sh maydonlarni to'ldirish
        if phone_number and not username:
            username = phone_number
        if username and not phone_number:
            phone_number = username

        # 3. Bazada bor-yo'qligini tekshirish
        existing = User.objects.filter(
            Q(username=username) | Q(phone_number=phone_number)
        )
        if existing.exists():
            raise serializers.ValidationError(
                {"error": "Ushbu telefon raqami yoki username allaqachon band!"}
            )

        # Yangilangan qiymatlarni attrs ga saqlash
        attrs['username'] = username
        attrs['phone_number'] = phone_number
        return attrs

    def create(self, validated_data):
        # 1. 6 talik raqamli parol generatsiya
        raw_password = str(random.randint(100000, 999999))

        # 2. Oxirgi xavfsizlik tekshiruvi
        if User.objects.filter(
            Q(username=validated_data['username']) | Q(phone_number=validated_data['phone_number'])
        ).exists():
            raise serializers.ValidationError(
                {"error": "Foydalanuvchi allaqachon mavjud!"}
            )

        # 3. User yaratish
        user = User(
            username=validated_data['username'],
            phone_number=validated_data['phone_number'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            department=validated_data.get('department'),
            description=validated_data.get('description', ''),
            role='MANAGER',
            is_staff=True,
            plain_password=raw_password,
        )
        user.set_password(raw_password)
        user.save()

        # 4. Response uchun ochiq parolni saqlash
        user._raw_password = raw_password
        return user

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'username': instance.username,
            'phone_number': instance.phone_number,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'role': instance.role,
            'department': instance.department.name if instance.department else None,
            'description': instance.description,
            'password': instance._raw_password,
        }

class ManagerListSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='department.name', default=None)
    password = serializers.CharField(source='plain_password', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number', 'first_name', 'last_name', 'department', 'description', 'password']

class EmployeeBulkCreateSerializer(serializers.Serializer):
    exam_id = serializers.PrimaryKeyRelatedField(
        queryset=Exam.objects.all(),
        source='exam'
    )
    file = serializers.FileField()

    def create(self, validated_data):
        file = validated_data.pop('file')
        exam = validated_data.pop('exam')

        wb = openpyxl.load_workbook(BytesIO(file.read()), read_only=True)
        ws = wb.active

        created_users = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row[0] and not row[1] and not row[2]:
                continue
            
            first_name = str(row[0]).strip() if row[0] else ''
            last_name = str(row[1]).strip() if row[1] else ''
            identity = str(row[2]).strip() if row[2] else ''
            position = str(row[3]).strip() if row[3] else ''

            # Identity logic
            if identity.isdigit():
                username = identity
                phone_number = identity
            else:
                username = identity
                phone_number = f"un_{random.randint(100000, 999999)}" # Unique phone placeholder if non-digit

            # 5 xonali parol
            raw_password = str(random.randint(10000, 99999))

            # Duplicate check
            if User.objects.filter(Q(username=username) | Q(phone_number=phone_number)).exists():
                continue

            user = User(
                username=username,
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                description=position, # Saving Position in description
                department=exam.department, # Auto assign from exam's department
                assigned_exam=exam, # Link to the exam
                role='EMPLOYEE',
                is_active=True,
                plain_password=raw_password
            )
            user.set_password(raw_password)
            user.save()
            user._raw_password = raw_password
            created_users.append(user)

        wb.close()
        return created_users

    def to_representation(self, instances):
        # Since it returns a list,เรา manually handle representation
        return [
            {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'phone_number': user.phone_number,
                'password': user._raw_password
            } for user in instances
        ]

class EmployeeListSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='department.name', default="Bo'lim biriktirilmagan")
    assigned_exam = serializers.SerializerMethodField()
    password = serializers.CharField(source='plain_password', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'username', 
            'phone_number', 'department', 'assigned_exam', 'password'
        ]

    @extend_schema_field(serializers.CharField())
    def get_assigned_exam(self, obj):
        if obj.assigned_exam:
            return obj.assigned_exam.title
        return "Test biriktirilmagan"
