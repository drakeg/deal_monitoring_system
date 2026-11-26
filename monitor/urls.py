from django.contrib import admin
from django.urls import path, include
from alerts.views import dashboard, delete_alert
urlpatterns = [path("", dashboard), path("alerts/<int:pk>/delete/", delete_alert), path("accounts/", include("django.contrib.auth.urls")), path("admin/", admin.site.urls)]

from alerts.campaigns import campaigns, toggle_campaign
urlpatterns += [path("campaigns/", campaigns, name="campaigns"), path("campaigns/<int:pk>/toggle/", toggle_campaign, name="toggle_campaign")]

from alerts.deals import deals
urlpatterns += [path("campaigns/<int:pk>/deals/", deals, name="deals")]
