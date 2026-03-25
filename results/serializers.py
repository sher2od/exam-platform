from rest_framework import serializers
from .models import Attempt
from drf_spectacular.utils import extend_schema_field


class StartExamSerializer(serializers.Serializer):
    exam_id = serializers.IntegerField()


class AnswerItemSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    option_id = serializers.IntegerField()


class SubmitExamSerializer(serializers.Serializer):
    attempt_id = serializers.IntegerField()
    answers = AnswerItemSerializer(many=True)


class AttemptResultSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(source='exam.title')
    username = serializers.CharField(source='user.username')

    class Meta:
        model = Attempt
        fields = [
            'id', 'username', 'exam_title',
            'total_questions', 'correct_answers', 'wrong_answers',
            'percentage', 'is_passed',
            'start_time', 'end_time',
        ]


class AttemptListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    exam = serializers.SerializerMethodField()

    class Meta:
        model = Attempt
        fields = [
            'id', 'user', 'exam', 'total_questions', 
            'correct_answers', 'wrong_answers', 'is_passed', 'start_time'
        ]

    @extend_schema_field(serializers.DictField())
    def get_user(self, obj):
        return {
            'full_name': f"{obj.user.first_name} {obj.user.last_name}",
            'username': obj.user.username,
            'phone_number': obj.user.phone_number
        }

    @extend_schema_field(serializers.DictField())
    def get_exam(self, obj):
        return {
            'title': obj.exam.title,
            'department': obj.exam.department.name if obj.exam.department else None
        }

class ManagerReportSerializer(serializers.Serializer):
    employee_name = serializers.CharField()
    exam_title = serializers.CharField()
    total_questions = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    wrong_answers = serializers.IntegerField()
    skipped_questions = serializers.IntegerField()
    time_spent = serializers.IntegerField()
