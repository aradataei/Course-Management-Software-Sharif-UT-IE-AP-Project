from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum

student_id_validator = RegexValidator(
    regex=r'^\d{9}$',
    message='Student ID must be a 9-digit number.'
)
class CustomUserManager(BaseUserManager):
    def create_user(self, student_id, password=None, **extra_fields):
        if not student_id:
            raise ValueError('The Student ID must be set')
        if len(str(student_id)) != 9:
            raise ValueError('Student ID must be a 9-digit number')
        
        user = self.model(student_id=student_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, student_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(student_id, password, **extra_fields)


class UserLevel(models.Model):
    user_level_name = models.CharField(max_length=100)

    def __str__(self):
        return self.user_level_name


class CustomUser(AbstractBaseUser, PermissionsMixin):
    student_id = models.BigIntegerField(
        primary_key=True,
        unique=True,
        validators=[student_id_validator],
        verbose_name='Student ID'
    )
    user_level = models.ForeignKey('UserLevel', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'student_id'
    REQUIRED_FIELDS = [] 

    def __str__(self):
        return str(self.student_id)


class Major(models.Model):
    major_name = models.CharField(max_length=30)

    def __str__(self):
        return self.major_name


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    national_id = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='کد ملی باید دقیقا ۱۰ رقم باشد.'
            )
        ]
    )
    
    phone_number = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+98\d{10}$',
                message='شماره تلفن باید به فرم +98XXXXXXXXXX باشد.'
            )
        ]
    )
    
    gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(20.0)
        ],
    )
    
    max_units = models.PositiveIntegerField(default=0, editable=False)
    
    email = models.EmailField(unique=True)
    major = models.ForeignKey('Major', on_delete=models.SET_NULL, null=True) 
    admission_year = models.PositiveIntegerField(default=1403, choices={
        1403: 1403,
        1402: 1402,
        1401: 1401,
        1400: 1400,
        1399: 1399,
        1398: 1388,
    })
    
    def save(self, *args, **kwargs):
        if self.gpa < 14:
            self.max_units = 16
        elif 14 <= self.gpa < 17:
            self.max_units = 20
        else:  # gpa >= 17
            self.max_units = 24
        super().save(*args, **kwargs)
    
    def clean(self):
        if not self.national_id.isdigit() or len(self.national_id) != 10:
            raise ValidationError({'national_id': 'کد ملی باید دقیقا ۱۰ رقم باشد.'})
        if self.phone_number:
            import re
            pattern = r'^\+98\d{10}$'
            if not re.match(pattern, self.phone_number):
                raise ValidationError({'phone_number': 'شماره تلفن باید به فرم +98XXXXXXXXXX باشد.'})
    
    def get_current_units(self):
        return self.studentcourse_set.aggregate(
            total=Sum('course__units')
        )['total'] or 0

    def can_enroll(self, new_units):
        return (self.get_current_units() + new_units) <= self.max_units

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Department(models.Model):
    department_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='نام دپارتمان',
        error_messages={
            'unique': 'این نام دپارتمان قبلاً ثبت شده است'
        }
    )
    
    def __str__(self):
        return self.department_name


class Professor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='instructors')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Classroom(models.Model):
    classroom_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.classroom_name



class Course(models.Model):
    course_name = models.CharField(max_length=200)
    course_code = models.CharField(max_length=50, unique=True)
    exam_time = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=10)  # ظرفیت اولیه
    remaining_capacity = models.PositiveIntegerField(default=0)  # ظرفیت باقی‌مانده
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True, blank=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True)
    corequisites = models.ManyToManyField('self', through='CoRequisite', symmetrical=False, related_name='corequired_for')
    units = models.PositiveIntegerField(default=3)
    major = models.ForeignKey(Major, related_name='majors', on_delete=models.SET_NULL, null=True, blank=True)

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


    def validate_max_two_days(value):
        days = [d.strip() for d in value.split(',')]
        
        if len(days) > 2:
            raise ValidationError('حداکثر 2 روز قابل انتخاب است')
        

        valid_days = [d[0] for d in Course.DAYS_OF_WEEK]
        for day in days:
            if day not in valid_days:
                raise ValidationError(f'روز نامعتبر: {day}')

    class_date = models.CharField(
    max_length=23,
    verbose_name="روزهای برگزاری کلاس",
    help_text="حداکثر 2 روز را با کاما جدا کنید (مثال: Sat,Mon)",
    validators=[validate_max_two_days]
    )

    class_time = models.CharField(
        max_length=11,
        choices=TIME_SLOTS,
        verbose_name="زمان برگزاری کلاس"
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.remaining_capacity = self.capacity
        super().save(*args, **kwargs)

    def clean(self):
        if self.class_date:
            dates = [day.strip() for day in self.class_date.split(',')]
            if not (1 <= len(dates) <= 2):
                raise ValidationError("شما باید حداقل یکی و حداکثر دو روز را انتخاب کنید.")
            valid_days = [day[0] for day in self.DAYS_OF_WEEK]
            for day in dates:
                if day not in valid_days:
                    raise ValidationError(f"{day} یک روز معتبر نیست.")
       
    def __str__(self):
        return self.course_name




class StudentCourse(models.Model):
    STATUS_CHOICES = (
        ('enrolled', 'Enrolled'),
        ('withdrawn', 'Withdrawn'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')

    class Meta:
        unique_together = ('student', 'course')

    def clean(self):
        if self.status == 'enrolled':
            for co_requisite in self.course.corequisites.all():
                if not StudentCourse.objects.filter(student=self.student, course=co_requisite.corequisite, status='enrolled').exists():
                    raise ValidationError(
                        f"You must enroll in {co_requisite.corequisite.course_name} as a co-requisite."
                    )
                
    def save(self, *args, **kwargs):
        is_new = self.pk is None 
        if is_new and self.status == 'enrolled':
            if self.course.remaining_capacity <= 0:
                raise ValidationError('Course capacity full.')
            self.course.remaining_capacity -= 1
            self.course.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.status == 'enrolled':
            self.course.remaining_capacity += 1
            self.course.save()
        super().delete(*args, **kwargs)
        def __str__(self):
            return f"{self.student} ثبت نام شد در {self.course}"



class CoRequisite(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='corequisites_set')
    required_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='required_corequisites')

    class Meta:
        unique_together = ('course', 'required_course')

    def __str__(self):
        return f"{self.required_course} هم نیاز است با {self.course}"




