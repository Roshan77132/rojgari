from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('files/resume/<int:pk>/', views.profile_resume, name='profile_resume'),
    path('files/company-doc/<int:pk>/', views.company_document, name='company_document'),
    path('about/', views.about_view, name='about'),
]