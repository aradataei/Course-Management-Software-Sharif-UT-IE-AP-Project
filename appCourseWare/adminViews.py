from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from .models import (
    Course, Student, StudentCourse, Professor,
    Department, Classroom, CustomUser, UserLevel,
    Major, Prerequisite, CoRequisite
)

# ------------------------ عمومی --------------------------
def get_model_fields(model):
    """تابع کمکی برای دریافت فیلدهای یک مدل"""
    return [field.name for field in model._meta.fields]

# ------------------------ مدیریت کاربران --------------------------
@staff_member_required
def manage_users_view(request):
    """مدیریت کاربران (تبدیل به ادمین/حذف ادمین)"""
    users = CustomUser.objects.all()
    user_levels = UserLevel.objects.all()
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(CustomUser, student_id=user_id)
        
        if action == 'make_admin':
            user.is_staff = True
            user.save()
            messages.success(request, 'کاربر با موفقیت ادمین شد')
        elif action == 'remove_admin':
            user.is_staff = False
            user.save()
            messages.success(request, 'ادمین با موفقیت حذف شد')
            
    return render(request, 'manager/manage_users.html', {
        'users': users,
        'user_levels': user_levels
    })

# ------------------------ مدیریت دانشجویان --------------------------
@staff_member_required
def student_list_view(request):
    """لیست تمام دانشجویان"""
    students = Student.objects.select_related('user', 'major').all()
    return render(request, 'manager/student_list.html', {'students': students})

@staff_member_required
def student_edit_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        # پردازش فیلد major به صورت جداگانه
        major_id = request.POST.get('major')
        if major_id:
            student.major = get_object_or_404(Major, pk=major_id)
        
        # بروزرسانی سایر فیلدها
        for field in get_model_fields(Student):
            if field in request.POST and field not in ['user', 'major']:  # exclude major
                setattr(student, field, request.POST.get(field))
        
        try:
            student.full_clean()  # اعتبارسنجی مدل
            student.save()
            messages.success(request, 'اطلاعات دانشجو با موفقیت بروزرسانی شد')
            return redirect('student_list_view')
        except ValidationError as e:
            messages.error(request, f'خطا در اعتبارسنجی: {e}')
    
    admission_years= ['1403','1402','1401','1400','1399','1398']

    majors = Major.objects.all()
    return render(request, 'manager/edit_student.html', {
        'student': student,
        'majors': majors,
        'admission_years': admission_years
    })

@staff_member_required
def student_delete_view(request, pk):
    """حذف دانشجو"""
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.user.delete()  # حذف کاربر مرتبط
        messages.success(request, 'دانشجو با موفقیت حذف شد')
        return redirect('student_list_view')
    return render(request, 'manager/confirm_delete.html', {'object': student})

# ------------------------ مدیریت اساتید --------------------------
@staff_member_required
def professor_list_view(request):
    """لیست تمام اساتید"""
    professors = Professor.objects.select_related('department').all()
    return render(request, 'manager/professor_list.html', {'professors': professors})

@staff_member_required
def professor_create_view(request):
    try:
        departments = Department.objects.all()
        if request.method == 'POST':
            # Validate required fields
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            department_id = request.POST.get('department')

            if not all([first_name, last_name, email, department_id]):
                raise ValidationError("لطفا تمام فیلدهای ضروری را پر کنید")

            # Check email uniqueness
            if Professor.objects.filter(email=email).exists():
                raise ValidationError("این ایمیل قبلاً ثبت شده است")

            department = Department.objects.get(pk=department_id)
            
            # Create professor
            professor = Professor.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                department=department
            )
            
            messages.success(request, 'استاد جدید با موفقیت ایجاد شد')
            return redirect('professor_list_view')

        return render(request, 'manager/create_professor.html', {
            'departments': departments
        })

    except Exception as e:
        messages.error(request, f'خطا در ایجاد استاد: {str(e)}')
        return redirect('professor_list_view')

@staff_member_required
def professor_edit_view(request, pk):
    """ویرایش اطلاعات استاد"""
    professor = get_object_or_404(Professor, pk=pk)
    
    if request.method == 'POST':
        for field in get_model_fields(Professor):
            if field in request.POST and field != 'professor.pk':
                if field == 'department':  # Check if field is department
                    department_id = request.POST.get(field)
                    department_instance = Department.objects.get(pk=department_id)
                    setattr(professor, field, department_instance)
                else:
                    setattr(professor, field, request.POST.get(field))

        professor.save()
        messages.success(request, 'اطلاعات استاد با موفقیت بروز‌رسانی شد')
        return redirect('professor_list_view')
    
    departments = Department.objects.all()
    return render(request, 'manager/edit_professor.html', {
        'professor': professor,
        'departments': departments
    })

@staff_member_required
def professor_delete_view(request, pk):
    """حذف استاد"""
    professor = get_object_or_404(Professor, pk=pk)
    if request.method == 'POST':
        professor.delete()
        messages.success(request, 'استاد با موفقیت حذف شد')
        return redirect('professor_list_view')
    return render(request, 'manager/confirm_delete.html', {'object': professor})

# ------------------------ مدیریت دپارتمان‌ها --------------------------
@staff_member_required
def department_list_view(request):
    departments = Department.objects.all()
    return render(request, 'manager/department_list.html', {'departments': departments})

@staff_member_required
def department_edit_view(request, pk=None):
    """ایجاد/ویرایش دپارتمان"""
    department = get_object_or_404(Department, pk=pk) if pk else None
    
    if request.method == 'POST':
        name = request.POST.get('department_name')
        if not name:
            messages.error(request, 'نام دپارتمان الزامی است')
            return redirect('department_list_view')
        
        if department:
            department.department_name = name
        else:
            department = Department(department_name=name)
        department.save()
        
        messages.success(request, 'دپارتمان با موفقیت ذخیره شد')
        return redirect('department_list_view')
    
    return render(request, 'manager/edit_department.html', {'department': department})

@staff_member_required
def department_delete_view(request, pk):
    try:
        department = Department.objects.get(pk=pk)
        if request.method == 'POST':
            department.delete()
            messages.success(request, 'دپارتمان با موفقیت حذف شد')
            return redirect('department_list_view')
        return render(request, 'manager/confirm_delete.html', {
            'object': department,
            'title': 'حذف دپارتمان',
            'back_url': reverse('department_list_view')
        })
    except Department.DoesNotExist:
        messages.error(request, 'دپارتمان مورد نظر یافت نشد')
        return redirect('department_list_view')
    
# ------------------------ مدیریت کلاس‌ها --------------------------
@staff_member_required
def classroom_list_view(request):
    classrooms = Classroom.objects.select_related('department').all()
    return render(request, 'manager/classroom_list.html', {'classrooms': classrooms})

@staff_member_required
def classroom_create_view(request):
    if request.method == 'POST':
        classroom_name = request.POST.get('classroom_name')
        department_id = request.POST.get('department_id')
        try:
            classroom = Classroom.objects.create(
                classroom_name=classroom_name,
                department_id=department_id
            )
            messages.success(request, 'کلاس با موفقیت ایجاد شد.')
            return redirect('classroom_list_view')
        except Exception as e:
            messages.error(request, f'خطا در ایجاد کلاس: {str(e)}')
    departments = Department.objects.all()
    return render(request, 'manager/edit_classroom.html', {
        'departments': departments,
        'classroom': None
    })


@staff_member_required
def classroom_edit_view(request, pk=None):
    """ایجاد/ویرایش کلاس"""
    classroom = get_object_or_404(Classroom, pk=pk) if pk else None
    
    if request.method == 'POST':
        name = request.POST.get('classroom_name')
        department_id = request.POST.get('department')
        
        if not all([name, department_id]):
            messages.error(request, 'تمامی فیلدها الزامی هستند')
            return redirect('classroom_list_view')
        
        department = get_object_or_404(Department, pk=department_id)
        
        if classroom:
            classroom.classroom_name = name
            classroom.department = department
        else:
            classroom = Classroom(classroom_name=name, department=department)
        classroom.save()
        
        messages.success(request, 'کلاس با موفقیت ذخیره شد')
        return redirect('classroom_list_view')
    
    departments = Department.objects.all()
    return render(request, 'manager/edit_classroom.html', {
        'classroom': classroom,
        'departments': departments
    })

@staff_member_required
def classroom_delete_view(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    if request.method == 'POST':
        try:
            classroom.delete()
            messages.success(request, 'کلاس با موفقیت حذف شد.')
        except Exception as e:
            messages.error(request, f'خطا در حذف کلاس: {str(e)}')
        return redirect('classroom_list_view')
    
    # اگر متد POST نبود یعنی کاربر هنوز فرم تایید را نفرستاده
    return render(request, 'manager/confirm_delete.html', {'object': classroom, 'type': 'کلاس'})

@staff_member_required
def course_list_view(request):
    courses = Course.objects.select_related(
        'department', 'professor', 'classroom'
    ).prefetch_related('prerequisites', 'corequisites').all()
    
    # Filtering logic
    department_filter = request.GET.get('department')
    if department_filter:
        courses = courses.filter(department__department_name=department_filter)
    
    return render(request, 'manager/course_list.html', {
        'courses': courses,
        'departments': Department.objects.all(),
        'classrooms': Classroom.objects.all(),
        'professors': Professor.objects.all()
    })

@staff_member_required
def course_create_view(request):
    try:
        departments = Department.objects.all()
        professors = Professor.objects.all()
        classrooms = Classroom.objects.all()
        majors = Major.objects.all()
        
        if request.method == 'POST':
            # دریافت تمامی فیلدهای مورد نیاز از مدل
            course_data = {
                'course_name': request.POST.get('course_name'),
                'course_code': request.POST.get('course_code'),
                'units': request.POST.get('units'),
                'exam_time': request.POST.get('exam_time'),
                'capacity': request.POST.get('capacity'),
                'class_date': request.POST.get('class_date'),
                'class_time': request.POST.get('class_time'),
                'department_id': request.POST.get('department'),
                'professor_id': request.POST.get('professor'),
                'classroom_id': request.POST.get('classroom'),
                'major_id': request.POST.get('major')
            }
            
            # اعتبارسنجی فیلدهای ضروری
            required_fields = ['course_name', 'units', 'department_id', 'professor_id', 'classroom_id']
            if not all(course_data[field] for field in required_fields):
                raise ValidationError("پر کردن فیلدهای ستاره‌دار الزامی است")
            
            # ایجاد دوره با تمامی فیلدهای مرتبط
            Course.objects.create(**course_data)
            
            messages.success(request, 'دوره جدید با موفقیت ساخته شد')
            return redirect('course_list_view')
        
        return render(request, 'manager/create_course.html', {
            'departments': departments,
            'professors': professors,
            'classrooms': classrooms,
            'time_slots': Course.TIME_SLOTS, # اضافه کردن این خط
            'majors': majors
        })
    
    except Exception as e:
        messages.error(request, f'خطا در ایجاد دوره: {str(e)}')
        return redirect('course_list_view')

@staff_member_required
def course_edit_view(request, pk):
    try:
        course = get_object_or_404(Course, pk=pk)
        departments = Department.objects.all()
        professors = Professor.objects.all()
        classrooms = Classroom.objects.all()
        majors = Major.objects.all()
        
        if request.method == 'POST':
            # دریافت و بروزرسانی تمامی فیلدها
            update_data = {
                'course_name': request.POST.get('course_name'),
                'course_code': request.POST.get('course_code'),
                'units': request.POST.get('units'),
                'exam_time': request.POST.get('exam_time'),
                'capacity': request.POST.get('capacity'),
                'class_date': request.POST.get('class_date'),
                'class_time': request.POST.get('class_time'),
                'department_id': request.POST.get('department'),
                'professor_id': request.POST.get('professor'),
                'classroom_id': request.POST.get('classroom'),
                'major_id': request.POST.get('major')
            }
            
            # اعتبارسنجی فیلدهای ضروری
            required_fields = ['course_name', 'units', 'department_id', 'professor_id', 'classroom_id']
            if not all(update_data[field] for field in required_fields):
                raise ValidationError("پر کردن فیلدهای ستاره‌دار الزامی است")
            
            # بروزرسانی شیء دوره
            for key, value in update_data.items():
                setattr(course, key, value)
            course.save()
            
            messages.success(request, 'تغییرات دوره با موفقیت ذخیره شد')
            return redirect('course_list_view')
        
        return render(request, 'manager/edit_course.html', {
            'course': course,
            'departments': departments,
            'professors': professors,
            'classrooms': classrooms,
            'time_slots': Course.TIME_SLOTS, # اضافه کردن این خط
            'majors': majors
        })
    
    except Exception as e:
        messages.error(request, f'خطا در ویرایش دوره: {str(e)}')
        return redirect('course_list_view')

@staff_member_required
def course_delete_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        try:
            course.delete()
            messages.success(request, 'درس با موفقیت حذف شد')
        except Exception as e:
            messages.error(request, f'خطا در حذف درس: {str(e)}')
        return redirect('course_list_view')
    return render(request, 'manager/confirm_delete.html', {'object': course})


@staff_member_required
def enroll_student_view(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                student_id = request.POST.get('student')
                course_ids = request.POST.getlist('courses')
                
                student = Student.objects.get(pk=student_id)
                courses = Course.objects.filter(pk__in=course_ids)
                
                # محاسبه مجموع واحدهای انتخابی
                total_units = courses.aggregate(total=Sum('units'))['total'] or 0
                current_units = StudentCourse.objects.filter(student=student).aggregate(total=Sum('course__units'))['total'] or 0
                
                # اعتبارسنجی حداکثر واحدها
                if (current_units + total_units) > student.max_units:
                    messages.error(request, f'مجموع واحدها از حد مجاز ({student.max_units}) بیشتر میشود!')
                    return redirect('enroll_student')
                
                # اعتبارسنجی پیش‌نیازها
                for course in courses:
                    prerequisites = course.prerequisites.all()
                    for prereq in prerequisites:
                        if not StudentCourse.objects.filter(student=student, course=prereq, status='completed').exists():
                            messages.error(request, f'درس {prereq.course_name} به عنوان پیش‌نیاز {course.course_name} گذرانده نشده است!')
                            return redirect('enroll_student')
                
                # اعتبارسنجی همنیازها
                for course in courses:
                    coreqs = course.corequisites.all()
                    for coreq in coreqs:
                        if coreq not in courses:
                            messages.error(request, f'درس {coreq.course_name} باید همزمان با {course.course_name} اخذ شود!')
                            return redirect('enroll_student')
                
                # ثبت نهایی دروس
                for course in courses:
                    StudentCourse.objects.create(
                        student=student,
                        course=course,
                        status='enrolled'
                    )
                
                messages.success(request, 'اخذ درس با موفقیت انجام شد!')
                return redirect('student_list_view')
        
        except Exception as e:
            messages.error(request, f'خطا در ثبت اطلاعات: {str(e)}')
            return redirect('enroll_student')

    students = Student.objects.all()
    courses = Course.objects.all()
    return render(request, 'manager/enroll_student.html', {
        'students': students,
        'courses': courses
    })

@staff_member_required
def major_list_view(request):
    majors = Major.objects.all().order_by('major_name')
    context = {
        'majors': majors,
        'page_title': 'مدیریت رشته‌های تحصیلی',
        'active_menu': 'academic-management'
    }
    return render(request, 'manager/major_list.html', context)

def major_edit_view(request, pk):
    pass

@staff_member_required
def corequisite_list_view(request):
    corequisites = CoRequisite.objects.select_related('course', 'required_course')
    context = {
        'corequisites': corequisites,
        'title': 'مدیریت همنیازها'
    }
    return render(request, 'manager/corequisite_list.html', context)

@staff_member_required
def corequisite_create_view(request):
    if request.method == 'POST':
        try:
            course_id = request.POST.get('course')
            required_course_id = request.POST.get('required_course')
            
            if course_id == required_course_id:
                messages.error(request, 'یک درس نمی‌تواند همنیاز خودش باشد')
                return redirect('corequisite_create_view')
            
            CoRequisite.objects.create(
                course_id=course_id,
                required_course_id=required_course_id
            )
            messages.success(request, 'همنیاز با موفقیت ایجاد شد')
            return redirect('corequisite_list_view')
            
        except Exception as e:
            messages.error(request, f'خطا در ایجاد همنیاز: {str(e)}')
    
    courses = Course.objects.all()
    return render(request, 'manager/corequisite_form.html', {'courses': courses})

@staff_member_required
def corequisite_edit_view(request, pk):
    corequisite = get_object_or_404(CoRequisite, pk=pk)
    
    if request.method == 'POST':
        try:
            course_id = request.POST.get('course')
            required_course_id = request.POST.get('required_course')
            
            if course_id == required_course_id:
                messages.error(request, 'یک درس نمی‌تواند همنیاز خودش باشد')
                return redirect('corequisite_edit_view', pk=pk)
            
            corequisite.course_id = course_id
            corequisite.required_course_id = required_course_id
            corequisite.save()
            
            messages.success(request, 'همنیاز با موفقیت ویرایش شد')
            return redirect('corequisite_list_view')
            
        except Exception as e:
            messages.error(request, f'خطا در ویرایش همنیاز: {str(e)}')
    
    courses = Course.objects.all()
    return render(request, 'manager/corequisite_form.html', {
        'corequisite': corequisite,
        'courses': courses
    })


@staff_member_required
def corequisite_delete_view(request, pk):
    corequisite = get_object_or_404(CoRequisite, pk=pk)
    if request.method == 'POST':
        try:
            corequisite.delete()
            messages.success(request, 'همنیازی با موفقیت حذف شد')
        except Exception as e:
            messages.error(request, f'خطا در حذف همنیازی: {str(e)}')
        return redirect('corequisite_list_view')
    return render(request, 'manager/confirm_delete.html', {'object': corequisite})
