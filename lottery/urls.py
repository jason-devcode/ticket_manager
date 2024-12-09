"""
URL configuration for lottery project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

from djangopwa.admin_custom_views import custom_admin_tickets_view, admin_reports_view

urlpatterns = [
    path('admin/reports', admin_reports_view, name='custom_admin_view'),
    path("admin/tickets-view/", custom_admin_tickets_view, name="admin-tickets-view"),
    path("admin/", admin.site.urls),
    path("", include("djangopwa.urls")),
    path("", include("pwa.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
]