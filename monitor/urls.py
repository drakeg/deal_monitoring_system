from django.contrib import admin
from django.urls import path, include
from alerts.views import dashboard, delete_alert
urlpatterns = [path("", dashboard), path("alerts/<int:pk>/delete/", delete_alert), path("accounts/", include("django.contrib.auth.urls")), path("admin/", admin.site.urls)]
