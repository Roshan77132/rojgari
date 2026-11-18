from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('mine/', views.my_applications, name='mine'),
    path('apply/<int:job_pk>/', views.apply, name='apply'),
    path('job/<int:job_pk>/', views.job_applicants, name='applicants'),
    path('<int:pk>/withdraw/', views.withdraw, name='withdraw'),
    path('<int:pk>/status/', views.update_status, name='status'),
    path('<int:pk>/resume/', views.resume_download, name='resume'),
]