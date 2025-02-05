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

    # PROFESSOR PANEL
    path('manager/professors/', adminViews.professor_list_view, name='professor_list_view'),
    path('manager/professors/edit/<int:pk>/', adminViews.professor_edit_view, name='professor_edit_view'),
    path('manager/professors/delete/<int:pk>/', adminViews.professor_delete_view, name='professor_delete_view'),
    path('manager/professors/create/', adminViews.professor_create_view, name='professor_create_view'),

    # DEPARTMENT SECTION
    path('manager/departments/', adminViews.department_list_view, name='department_list_view'),
    path('manager/departments/create/', adminViews.department_edit_view, name='department_create'),
    path('manager/departments/delete/<int:pk>/', adminViews.department_delete_view, name='department_delete_view'),
    path('manager/departments/edit/<int:pk>/', adminViews.department_edit_view, name='department_edit_view'),    

    # CLASSROOM SECTION
    path('manager/classrooms/', adminViews.classroom_list_view, name='classroom_list_view'),
    path('manager/classrooms/create/', adminViews.classroom_create_view, name='classroom_create_view'),  # مسیر ایجاد
    path('manager/classrooms/edit/<int:pk>/', adminViews.classroom_edit_view, name='classroom_edit_view'),
    path('manager/classrooms/delete/<int:pk>/', adminViews.classroom_delete_view, name='classroom_delete_view'),  # مسیر حذف

    # Course Management
    path('manager/courses/', adminViews.course_list_view, name='course_list_view'),
    path('manager/courses/create/', adminViews.course_create_view, name='course_create_view'),
    path('manager/courses/edit/<int:pk>/', adminViews.course_edit_view, name='course_edit_view'),
    path('manager/courses/delete/<int:pk>/', adminViews.course_delete_view, name='course_delete_view'),
    
    path('manager/enroll-student/', adminViews.enroll_student_view, name='enroll_student'),

    path('manager/majors/', adminViews.major_list_view, name='major_list_view'),
    path('manager/majors/edit/<int:pk>/', adminViews.major_edit_view, name='major_edit_view'),

]