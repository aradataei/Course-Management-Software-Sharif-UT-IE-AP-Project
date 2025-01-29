from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('complete-profile/', views.CompleteProfileView.as_view(), name='complete-profile'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

]