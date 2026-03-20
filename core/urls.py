from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # API paths v1
    path('api/v1/users/', include('users.urls')),
    path('api/v1/departments/', include('departments.urls')),
    path('api/v1/exams/', include('exams.urls')),
    path('api/v1/results/', include('results.urls')),
    path('api/v1/attendance/', include('attendance.urls')),

    # Swagger / OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
