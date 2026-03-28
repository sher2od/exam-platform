from django.urls import path
from .views import (
    StartExamAPIView, 
    SubmitExamAPIView, 
    ResultListAPIView, 
    ManagerDepartmentResultsAPIView,
    AttemptDetailAPIView
)

urlpatterns = [
    path('start/', StartExamAPIView.as_view(), name='start-exam'),
    path('submit/', SubmitExamAPIView.as_view(), name='submit-exam'),
    path('all/', ResultListAPIView.as_view(), name='results-all'),
    path('all/<int:pk>/', AttemptDetailAPIView.as_view(), name='result-detail'),
    path('manager-report/', ManagerDepartmentResultsAPIView.as_view(), name='manager-report'),
]
