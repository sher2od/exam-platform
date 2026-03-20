from django.urls import path
from .views import CheckInAPIView, AttendanceListAPIView

urlpatterns = [
    path('check-in/', CheckInAPIView.as_view(), name='attendance-check-in'),
    path('list/', AttendanceListAPIView.as_view(), name='attendance-list'),
]
