from django.urls import path
from .views import (
    LoginAPIView, 
    ManagerCreateAPIView, 
    ManagerListAPIView, 
    ManagerDeleteAPIView,
    EmployeeBulkCreateAPIView,
    EmployeeListAPIView,
    EmployeeDeleteAPIView
)

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('create-manager/', ManagerCreateAPIView.as_view(), name='create-manager'),
    path('managers/', ManagerListAPIView.as_view(), name='manager-list'),
    path('managers/<int:pk>/delete/', ManagerDeleteAPIView.as_view(), name='manager-delete'),
    path('bulk-create-employees/', EmployeeBulkCreateAPIView.as_view(), name='bulk-create-employees'),
    path('employees/', EmployeeListAPIView.as_view(), name='employee-list'),
    path('employees/<int:pk>/delete/', EmployeeDeleteAPIView.as_view(), name='employee-delete'),
]
