from django.urls import path
from . import views, adminViews

urlpatterns = [
    # USER
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('create-student-profile/', views.create_student_profile, name='create_student_profile'),

    # ADMIN PANEL
    path('manager/manage-users/', adminViews.manage_users_view, name='manage_users'),
    path('manager/students/', adminViews.student_list_view, name='student_list_view'),
    path('manager/students/edit/<int:pk>/', adminViews.student_edit_view, name='student_edit_view'),
    path('manager/students/delete/<int:pk>/', adminViews.student_delete_view, name='student_delete_view'),
    path('manager/professors/', adminViews.professor_list_view, name='professor_list_view'),
    path('manager/professors/edit/<int:pk>/', adminViews.professor_edit_view, name='professor_edit_view'),
    path('manager/professors/delete/<int:pk>/', adminViews.professor_delete_view, name='professor_delete_view'),
    path('manager/departments/', adminViews.department_list_view, name='department_list_view'),
    path('manager/departments/edit/<int:pk>/', adminViews.department_edit_view, name='department_edit_view'),
    path('manager/classrooms/', adminViews.classroom_list_view, name='classroom_list_view'),
    path('manager/classrooms/edit/<int:pk>/', adminViews.classroom_edit_view, name='classroom_edit_view'),

    # Course Management
    path('manager/courses/', adminViews.course_list_view, name='course_list_view'),
    path('manager/courses/create/', adminViews.course_create_view, name='course_create_view'),
    path('manager/courses/edit/<int:pk>/', adminViews.course_edit_view, name='course_edit_view'),
    path('manager/courses/delete/<int:pk>/', adminViews.course_delete_view, name='course_delete_view'),
    path('manager/courses/<int:course_id>/prerequisites/', 
         adminViews.manage_prerequisites_view, name='manage_prerequisites'),
    
]