from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('create-student-profile/', views.create_student_profile, name='create_student_profile'),
]