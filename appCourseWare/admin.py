from django.contrib import admin
from .models import UserLevel, CustomUser, Student, Department, Instructor, Classroom, Course, Enrollment, Prerequisite, CoRequisite, CourseClassroom

admin.site.register(UserLevel)
admin.site.register(CustomUser)
admin.site.register(Department)
admin.site.register(Instructor)
admin.site.register(Classroom)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Prerequisite)
admin.site.register(CoRequisite)
admin.site.register(CourseClassroom)
admin.site.register(Student)
