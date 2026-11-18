from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_redirect, name='home'),
    path('company/', views.company_dashboard, name='company'),
    path('jobseeker/', views.jobseeker_dashboard, name='jobseeker'),
    path('jobseeker/edit/', views.jobseeker_edit, name='jobseeker_edit'),
    path('company/edit/', views.company_edit, name='company_edit'),
]