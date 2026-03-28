from django.urls import path
from .views import (
    ExamCreateAPIView, 
    ExamListAPIView, 
    ExamDeleteAPIView,
    ExamRetrieveAPIView,
    EmployeeExamQuestionsAPIView
)

urlpatterns = [
    path('create/', ExamCreateAPIView.as_view(), name='exam-create'),
    path('', ExamListAPIView.as_view(), name='exam-list'),
    path('<int:pk>/', ExamRetrieveAPIView.as_view(), name='exam-detail'),
    path('<int:pk>/delete/', ExamDeleteAPIView.as_view(), name='exam-delete'),
    path('my-questions/', EmployeeExamQuestionsAPIView.as_view(), name='my-questions'),
]
