from django.contrib import admin
from .models import UserLevel, CustomUser, Student, Department, Instructor, Classroom, Course, StudentCourse, Prerequisite, CoRequisite, Major

admin.site.register(UserLevel)
admin.site.register(CustomUser)
admin.site.register(Department)
admin.site.register(Instructor)
admin.site.register(Classroom)
admin.site.register(Course)
admin.site.register(StudentCourse)
admin.site.register(Prerequisite)
admin.site.register(CoRequisite)
admin.site.register(Student)
admin.site.register(Major)