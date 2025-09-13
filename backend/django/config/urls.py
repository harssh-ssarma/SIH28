from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/courses/', include('apps.courses.urls')),
    path('api/v1/classrooms/', include('apps.classrooms.urls')),
    path('api/v1/timetables/', include('apps.timetables.urls')),
    path('api/v1/approvals/', include('apps.approvals.urls')),
    path('api/v1/preferences/', include('apps.preferences.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
]