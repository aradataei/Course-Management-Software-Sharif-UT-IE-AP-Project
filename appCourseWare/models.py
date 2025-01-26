from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


# مدیریت سفارشی برای مدل کاربر
class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, user_level=None, **extra_fields):
        if not username:
            raise ValueError('Users must have a username')
        user = self.model(username=username, user_level=user_level, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, user_level=None, **extra_fields):
        user = self.create_user(username, password, user_level, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# 1. جدول UserLevels
class UserLevel(models.Model):
    user_level_id = models.AutoField(primary_key=True)
    user_level_name = models.CharField(max_length=100)

    def __str__(self):
        return self.user_level_name


# 2. جدول Users (مدل کاربر سفارشی)
class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    user_level = models.ForeignKey(UserLevel, on_delete=models.CASCADE, related_name='users', null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


# 3. جدول Students
class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    national_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    major = models.CharField(max_length=100)
    year = models.IntegerField()
    max_units = models.DecimalField(max_digits=5, decimal_places=2)
    student_number = models.CharField(max_length=20, unique=True)
    admission_year = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# 4. جدول Departments
class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100)

    def __str__(self):
        return self.department_name


# 5. جدول Instructors
class Instructor(models.Model):
    instructor_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='instructors')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# 7. جدول Classrooms
class Classroom(models.Model):
    classroom_id = models.AutoField(primary_key=True)
    classroom_name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='classrooms')

    def __str__(self):
        return self.classroom_name


# 6. جدول Courses
class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=200)
    course_code = models.CharField(max_length=50, unique=True)
    credits = models.DecimalField(max_digits=4, decimal_places=2)
    class_time = models.CharField(max_length=100)  # می‌توانید به TimeField تغییر دهید اگر لازم است
    exam_time = models.DateTimeField()
    capacity = models.IntegerField()
    remaining_capacity = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, related_name='courses')

    prerequisites = models.ManyToManyField('self', through='Prerequisite',
                                           symmetrical=False, related_name='required_for')
    corequisites = models.ManyToManyField('self', through='CoRequisite',
                                          symmetrical=False, related_name='corequired_for')
    classrooms = models.ManyToManyField(Classroom, through='CourseClassroom', related_name='courses')

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


# 8. جدول Enrollments
class Enrollment(models.Model):
    enrollment_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=50)  # به عنوان مثال: "Enrolled", "Waitlisted"

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"


# 9. جدول WeeklySchedule
class WeeklySchedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='weekly_schedules')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='weekly_schedules')
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]
    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.course} on {self.get_day_of_week_display()} from {self.start_time} to {self.end_time}"


# 10. جدول Prerequisites
class Prerequisite(models.Model):
    prerequisite_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='prerequisites_set')
    required_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='required_prerequisites')

    class Meta:
        unique_together = ('course', 'required_course')

    def __str__(self):
        return f"{self.required_course} is a prerequisite for {self.course}"


# 11. جدول CoRequisites
class CoRequisite(models.Model):
    corequisite_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='corequisites_set')
    required_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='required_corequisites')

    class Meta:
        unique_together = ('course', 'required_course')

    def __str__(self):
        return f"{self.required_course} is a corequisite for {self.course}"


# 12. جدول CourseClassrooms
class CourseClassroom(models.Model):
    course_classroom_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_classrooms')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='course_classrooms')

    class Meta:
        unique_together = ('course', 'classroom')

    def __str__(self):
        return f"{self.course} is held in {self.classroom}"


# تنظیمات مدل کاربر سفارشی باید در settings.py به شکل زیر باشد:
# AUTH_USER_MODEL = 'your_app_name.CustomUser'

