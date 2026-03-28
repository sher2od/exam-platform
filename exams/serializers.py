from rest_framework import serializers
from .models import Exam, Question, Option
from departments.models import Department
import openpyxl
from io import BytesIO
from drf_spectacular.utils import extend_schema_field


class ExamCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department'
    )
    duration = serializers.IntegerField(help_text="Daqiqalarda")
    passing_score = serializers.IntegerField(default=35, help_text="O'tish uchun minimal to'g'ri javoblar soni")
    file = serializers.FileField(help_text="Excel fayl (.xlsx): A-Savol, B-To'g'ri javob, C/D/E-Xato javoblar")

    def create(self, validated_data):
        file = validated_data.pop('file')
        department = validated_data.pop('department')

        # 1. Exam yaratish
        exam = Exam.objects.create(
            title=validated_data['title'],
            department=department,
            duration=validated_data['duration'],
            passing_score=validated_data.get('passing_score', 35),
        )

        # 2. Excel faylni RAM'da o'qish (serverga saqlamasdan)
        wb = openpyxl.load_workbook(BytesIO(file.read()), read_only=True)
        ws = wb.active

        questions_to_create = []

        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row[0]:  # Bo'sh qator bo'lsa o'tkazib yuborish
                continue

            question_text = str(row[0]).strip()
            correct_answer = str(row[1]).strip() if len(row) > 1 and row[1] else None
            wrong_1 = str(row[2]).strip() if len(row) > 2 and row[2] else None
            wrong_2 = str(row[3]).strip() if len(row) > 3 and row[3] else None
            wrong_3 = str(row[4]).strip() if len(row) > 4 and row[4] else None

            questions_to_create.append({
                'text': question_text,
                'options': []
            })

            # B ustun — To'g'ri javob
            if correct_answer:
                questions_to_create[-1]['options'].append({'text': correct_answer, 'is_correct': True})
            # C, D, E ustunlar — Xato javoblar
            if wrong_1:
                questions_to_create[-1]['options'].append({'text': wrong_1, 'is_correct': False})
            if wrong_2:
                questions_to_create[-1]['options'].append({'text': wrong_2, 'is_correct': False})
            if wrong_3:
                questions_to_create[-1]['options'].append({'text': wrong_3, 'is_correct': False})

        wb.close()

        # 3. Savollarni bulk_create bilan yaratish
        question_objects = Question.objects.bulk_create([
            Question(exam=exam, text=q['text']) for q in questions_to_create
        ])

        # 4. Variantlarni bulk_create bilan yaratish
        option_objects = []
        for i, question in enumerate(question_objects):
            for opt in questions_to_create[i]['options']:
                option_objects.append(
                    Option(question=question, text=opt['text'], is_correct=opt['is_correct'])
                )

        Option.objects.bulk_create(option_objects)

        # Statistikani qaytarish uchun
        exam._stats = {
            'questions_count': len(question_objects),
            'options_count': len(option_objects),
        }
        return exam

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'title': instance.title,
            'department': instance.department.name,
            'duration': instance.duration,
            'passing_score': instance.passing_score,
            'questions_count': instance._stats['questions_count'],
            'options_count': instance._stats['options_count'],
            'message': 'Test muvaffaqiyatli yuklandi!',
        }


class ExamListSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='department.name')
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ['id', 'title', 'department', 'duration', 'passing_score', 'questions_count']

    @extend_schema_field(serializers.IntegerField())
    def get_questions_count(self, obj):
        return obj.questions.count()


# --- Xodimlar uchun Anti-Cheat Serializers ---

class OptionEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text']


class QuestionEmployeeSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'text', 'options']

    @extend_schema_field(OptionEmployeeSerializer(many=True))
    def get_options(self, obj):
        # Variantlarni savol uchun random (shuffled) tartibda qaytarish
        options = Option.objects.filter(question=obj).order_by('?')
        return OptionEmployeeSerializer(options, many=True).data

# --- Admin serializers for Viewing questions ---

class OptionAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']

class QuestionAdminSerializer(serializers.ModelSerializer):
    options = OptionAdminSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['id', 'text', 'options']
