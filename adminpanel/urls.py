from django.urls import path

from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('companies/', views.companies, name='companies'),
    path('companies/<int:pk>/verify/', views.company_verify, name='company_verify'),
    path('companies/<int:pk>/reject/', views.company_reject, name='company_reject'),
    path('users/', views.users, name='users'),
    path('users/<int:pk>/toggle/', views.user_toggle, name='user_toggle'),
    path('jobs/', views.jobs, name='jobs'),
    path('jobs/<int:pk>/toggle/', views.job_toggle, name='job_toggle'),
]
