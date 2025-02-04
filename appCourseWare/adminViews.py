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
    
    majors = Major.objects.all()
    return render(request, 'manager/edit_student.html', {
        'student': student,
        'majors': majors
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
            if field in request.POST and field != 'instructor_id':
                setattr(professor, field, request.POST.get(field))
        professor.save()
        messages.success(request, 'اطلاعات استاد با موفقیت بروزرسانی شد')
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

# ------------------------ مدیریت پیشنیازها --------------------------
@staff_member_required
def manage_prerequisites_view(request, course_id):
    """مدیریت پیشنیازها و همنیازهای یک درس"""
    course = get_object_or_404(Course, pk=course_id)
    all_courses = Course.objects.exclude(pk=course_id)
    
    if request.method == 'POST':
        # مدیریت پیشنیازها
        prerequisite_ids = request.POST.getlist('prerequisites')
        for pid in prerequisite_ids:
            prereq = get_object_or_404(Course, pk=pid)
            Prerequisite.objects.get_or_create(course=course, required_course=prereq)
        
        # مدیریت همنیازها
        corequisite_ids = request.POST.getlist('corequisites')
        for cid in corequisite_ids:
            coreq = get_object_or_404(Course, pk=cid)
            CoRequisite.objects.get_or_create(course=course, required_course=coreq)
        
        messages.success(request, 'وابستگی‌ها با موفقیت بروزرسانی شدند')
        return redirect('course_detail_view', pk=course_id)
    
    return render(request, 'manager/manage_dependencies.html', {
        'course': course,
        'all_courses': all_courses
    })


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
    if request.method == 'POST':
        try:
            # Main course data
            course = Course.objects.create(
                course_name=request.POST['course_name'],
                course_code=request.POST['course_code'],
                department_id=request.POST['department'],
                professor_id=request.POST.get('professor'),
                classroom_id=request.POST.get('classroom'),
                capacity=request.POST['capacity'],
                class_date=request.POST.get('class_date', ''),
                class_time=request.POST.get('class_time', ''),
                exam_time=request.POST['exam_time']
            )
            
            # Handle prerequisites and corequisites
            prerequisites = request.POST.getlist('prerequisites')
            corequisites = request.POST.getlist('corequisites')
            
            Prerequisite.objects.bulk_create([
                Prerequisite(course=course, prerequisite_id=p_id) 
                for p_id in prerequisites
            ])
            
            CoRequisite.objects.bulk_create([
                CoRequisite(course=course, corequisite_id=c_id) 
                for c_id in corequisites
            ])
            
            messages.success(request, 'درس جدید با موفقیت ایجاد شد')
            return redirect('course_list_view')
            
        except Exception as e:
            messages.error(request, f'خطا در ایجاد درس: {str(e)}')
    
    return render(request, 'manager/course_edit.html', {
        'departments': Department.objects.all(),
        'professors': Professor.objects.all(),
        'classrooms': Classroom.objects.all(),
        'all_courses': Course.objects.exclude(
            course_code=request.POST.get('course_code')
        )
    })

@staff_member_required
def course_edit_view(request, pk=None):
    course = get_object_or_404(Course, pk=pk) if pk else None
    
    if request.method == 'POST':
        try:
            # Update basic course info
            course.course_name = request.POST['course_name']
            course.department_id = request.POST['department']
            course.professor_id = request.POST.get('professor')
            course.classroom_id = request.POST.get('classroom')
            course.capacity = request.POST['capacity']
            course.class_date = request.POST.get('class_date', '')
            course.class_time = request.POST.get('class_time', '')
            course.exam_time = request.POST['exam_time']
            course.full_clean()
            course.save()
            
            # Update prerequisites
            current_prerequisites = set(course.prerequisites.values_list('id', flat=True))
            new_prerequisites = set(map(int, request.POST.getlist('prerequisites')))
            
            # Remove obsolete prerequisites
            Prerequisite.objects.filter(
                course=course, 
                prerequisite_id__in=current_prerequisites - new_prerequisites
            ).delete()
            
            # Add new prerequisites
            new_prereq_ids = new_prerequisites - current_prerequisites
            Prerequisite.objects.bulk_create([
                Prerequisite(course=course, prerequisite_id=p_id) 
                for p_id in new_prereq_ids
            ])
            
            # Update corequisites (same logic as prerequisites)
            current_corequisites = set(course.corequisites.values_list('id', flat=True))
            new_corequisites = set(map(int, request.POST.getlist('corequisites')))
            
            CoRequisite.objects.filter(
                course=course, 
                corequisite_id__in=current_corequisites - new_corequisites
            ).delete()
            
            new_coreq_ids = new_corequisites - current_corequisites
            CoRequisite.objects.bulk_create([
                CoRequisite(course=course, corequisite_id=c_id) 
                for c_id in new_coreq_ids
            ])
            
            messages.success(request, 'تغییرات درس با موفقیت ذخیره شد')
            return redirect('course_list_view')
            
        except Exception as e:
            messages.error(request, f'خطا در ویرایش درس: {str(e)}')
    
    return render(request, 'manager/course_edit.html', {
        'course': course,
        'departments': Department.objects.all(),
        'professors': Professor.objects.all(),
        'classrooms': Classroom.objects.all(),
        'all_courses': Course.objects.exclude(id=course.id) if course else Course.objects.all(),
        'selected_prerequisites': course.prerequisites.values_list('id', flat=True) if course else [],
        'selected_corequisites': course.corequisites.values_list('id', flat=True) if course else []
    })

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