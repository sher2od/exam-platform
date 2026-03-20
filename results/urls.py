from django.urls import path
from .views import StartExamAPIView, SubmitExamAPIView, ResultListAPIView

urlpatterns = [
    path('start/', StartExamAPIView.as_view(), name='start-exam'),
    path('submit/', SubmitExamAPIView.as_view(), name='submit-exam'),
    path('all/', ResultListAPIView.as_view(), name='results-all'),
]
