from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
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

# ------------------------ مدیریت کلاس‌ها --------------------------
@staff_member_required
def classroom_list_view(request):
    classrooms = Classroom.objects.select_related('department').all()
    return render(request, 'manager/classroom_list.html', {'classrooms': classrooms})

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