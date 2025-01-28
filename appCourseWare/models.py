from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

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
    STUDENT_ID_MIN = 100000000  # حداقل مقدار ده رقمی
    STUDENT_ID_MAX = 403999999  # حداکثر مقدار ده رقمی
    student_id = models.BigIntegerField(
        primary_key=True,
        validators=[
            MinValueValidator(STUDENT_ID_MIN),
            MaxValueValidator(STUDENT_ID_MAX)
        ],
        unique=True,
        editable=True
    )
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    national_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    major = models.CharField(max_length=100)
    year = models.IntegerField()
    max_units = models.DecimalField(max_digits=5, decimal_places=2)
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
    capacity = models.PositiveIntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.classroom_name

# 6. جدول Courses
class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=200)
    course_code = models.CharField(max_length=50, unique=True)
    credits = models.DecimalField(max_digits=4, decimal_places=2)
    exam_time = models.DateTimeField()
    capacity = models.IntegerField(null=True, blank=True),
    remaining_capacity = models.PositiveIntegerField(null=True, blank=True)  # Calculated field
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, blank=True)
    prerequisites = models.ManyToManyField('self', symmetrical=False, related_name='prerequisites_set')
    corequisites = models.ManyToManyField('self', symmetrical=False, related_name='corequisites_set')
    classrooms = models.ManyToManyField(Classroom, through='CourseClassroom')

    prerequisites = models.ManyToManyField('self', through='Prerequisite',
                                           symmetrical=False, related_name='required_for')
    corequisites = models.ManyToManyField('self', through='CoRequisite',
                                          symmetrical=False, related_name='corequired_for')
    classrooms = models.ManyToManyField(Classroom, through='CourseClassroom', related_name='courses')

    DAYS_OF_WEEK = [
        ('Sat', 'شنبه'),
        ('Sun', 'یکشنبه'),
        ('Mon', 'دوشنبه'),
        ('Tue', 'سه‌شنبه'),
        ('Wed', 'چهارشنبه'),
    ]
    TIME_SLOTS = [
        ('8:00-10:00', '8:00-10:00'),
        ('10:00-12:00', '10:00-12:00'),
        ('14:00-16:00', '14:00-16:00'),
        ('16:00-18:00', '16:00-18:00'),
    ]

    class_date = models.CharField(
        max_length=23,  # حداکثر طول برای دو روز جدا شده با کاما
        help_text="یکی یا دو روز از شنبه تا چهارشنبه را انتخاب کنید. (مثال: Sat,Mon)",
        verbose_name="روزهای برگزاری کلاس",
        default="Sat"
    )
    
    class_time = models.CharField(
        max_length=11,
        choices=TIME_SLOTS,
        verbose_name="زمان برگزاری کلاس"
    )

    def clean(self):
        # اعتبارسنجی روزهای انتخاب شده
        if self.class_date:
            # جدا کردن روزها بر اساس کاما و حذف فاصله‌های اضافی
            dates = [day.strip() for day in self.class_date.split(',')]
            # بررسی تعداد روزهای انتخاب شده
            if not (1 <= len(dates) <= 2):
                raise ValidationError("شما باید حداقل یکی و حداکثر دو روز را انتخاب کنید.")
            # بررسی اعتبار هر روز انتخاب شده
            valid_days = [day[0] for day in self.DAYS_OF_WEEK]
            for day in dates:
                if day not in valid_days:
                    raise ValidationError(f"{day} یک روز معتبر نیست.")
                
    @property
    def enrolled_count(self):
        return self.enrollment_set.filter(status='enrolled').count()


    @property
    def remaining_capacity(self):
        enrolled_count = self.enrollment_set.filter(status='enrolled').count()
        return self.capacity - 1


    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


# 8. جدول Enrollments
class Enrollment(models.Model):
    enrollment_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(
        ('enrolled', 'در حال گذراندن'),
        ('dropped', 'افتاده'),
        ('withdrawed', 'حذف اضطراری'),      
        ('completed', 'گذرانده'),
    ))

    class Meta:
        unique_together = ('student', 'course')

    def save(self, *args, **kwargs):
        if self.course.remaining_capacity > 0:
            super().save(*args, **kwargs)
        else:
            raise ValueError("No remaining capacity for this course.")
                
    def __str__(self):
        return f"{self.student} ثبت نام شد در {self.course}"


# 10. جدول Prerequisites
class Prerequisite(models.Model):
    prerequisite_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='prerequisites_set')
    required_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='required_prerequisites')

    class Meta:
        unique_together = ('course', 'required_course')

    def __str__(self):
        return f"درس {self.required_course} پیش نیاز {self.course} است"


# 11. جدول CoRequisites
class CoRequisite(models.Model):
    corequisite_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='corequisites_set')
    required_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='required_corequisites')

    class Meta:
        unique_together = ('course', 'required_course')

    def __str__(self):
        return f"{self.required_course} هم نیاز است با {self.course}"


# 12. جدول CourseClassrooms
class CourseClassroom(models.Model):
    course_classroom_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_classrooms')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='course_classrooms')

    class Meta:
        unique_together = ('course', 'classroom')

    def __str__(self):
        return f"{self.course} برگزار میشود در کلاس {self.classroom}"



