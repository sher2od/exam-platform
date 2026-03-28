from rest_framework import serializers
from .models import Attendance
from drf_spectacular.utils import extend_schema_field

class AttendanceSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.SerializerMethodField()
    exam_title = serializers.CharField(source='exam.title', read_only=True)
    exam_duration = serializers.IntegerField(source='exam.duration', read_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id', 'user', 'username', 'full_name', 'exam',
            'exam_title', 'exam_duration', 'status', 'ip_address',
            'device_info', 'created_at'
        ]

    @extend_schema_field(serializers.CharField())
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
