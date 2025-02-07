from django.contrib import admin
from .models import UserLevel, CustomUser, Student, Department, Professor, Classroom, Course, StudentCourse, CoRequisite, Major

admin.site.register(UserLevel)
admin.site.register(CustomUser)
admin.site.register(Department)
admin.site.register(Professor)
admin.site.register(Classroom)
admin.site.register(Course)
admin.site.register(StudentCourse)
admin.site.register(CoRequisite)
admin.site.register(Student)
admin.site.register(Major)