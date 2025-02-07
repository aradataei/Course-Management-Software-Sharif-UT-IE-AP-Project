from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required
from .models import Course, Department, Student, StudentCourse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError

@login_required
def home_view(request):
    
    student = Student.objects.get(user=request.user)
    session = request.session
    
    if 'selected_courses' not in session:
        session['selected_courses'] = []
        session.modified = True
    
    if request.method == 'POST':
        if 'add_course' in request.POST:
            course_id = request.POST.get('course_id')
            return handle_add_course(request, course_id, student)
        
        if 'remove_course' in request.POST:
            course_id = request.POST.get('course_id')
            return handle_remove_course(request, course_id)
        
        if 'finalize' in request.POST:
            return handle_finalize(request, student)
    
    courses = filter_courses(request)
    
    current_units = StudentCourse.objects.filter(
        student=student, 
        status='enrolled'
    ).aggregate(Sum('course__units'))['course__units__sum'] or 0
    
    selected_units = Course.objects.filter(
        id__in=session['selected_courses']
    ).aggregate(Sum('units'))['units__sum'] or 0
    
    context = {
        'courses': courses.prefetch_related('corequisites'),
        'departments': Department.objects.all(),
        'current_units': current_units,
        'selected_units': selected_units,
        'max_units': student.max_units,
        'remaining_units': student.max_units - (current_units + selected_units),
        'selected_courses': Course.objects.filter(id__in=session['selected_courses']),
        'enrolled_courses': StudentCourse.objects.filter(student=student, status='enrolled')
    }
    
    return render(request, 'student/home.html', context)

def filter_courses(request):
    courses = Course.objects.filter(remaining_capacity__gt=0)
    
    department = request.GET.get('department')
    if department and department != 'all':
        courses = courses.filter(department__department_name=department)
    
    search = request.GET.get('search')
    if search:
        courses = courses.filter(
            Q(course_code__icontains=search) |
            Q(course_name__icontains=search)
        )
    
    return courses

def handle_add_course(request, course_id, student):
    course = get_object_or_404(Course, pk=course_id)
    session = request.session
    
    if has_time_conflict(student, course):
        messages.error(request, f'تداخل زمانی با {course.course_name}')
        return redirect('home_view')
    
    new_units = sum_units(student, session['selected_courses']) + course.units
    if new_units > student.max_units:
        messages.error(request, 'تعداد واحد مجاز превыشده')
        return redirect('home_view')
    
    current_units = StudentCourse.objects.filter(
        student=student, 
        status='enrolled'
    ).aggregate(Sum('course__units'))['course__units__sum'] or 0
    selected_units = sum_units(student, session['selected_courses'])
    total_units = current_units + selected_units + course.units

    if total_units > student.max_units:
        messages.error(request, 'تعداد واحد مجاز رد شده')
        return redirect('home_view')

    if course_id not in session['selected_courses']:
        session['selected_courses'].append(course_id)
        session.modified = True
        messages.success(request, f'{course.course_name} به سبد اضافه شد')
    


    return redirect('home_view')

def handle_remove_course(request, course_id):
    session = request.session
    if course_id in session['selected_courses']:
        session['selected_courses'].remove(course_id)
        session.modified = True
        messages.success(request, 'دوره با موفقیت حذف شد')
    return redirect('home_view')

def handle_finalize(request, student):
    with transaction.atomic():
        selected_courses = Course.objects.filter(
            id__in=request.session['selected_courses']
        )
        
        if has_time_conflict_in_list(selected_courses):
            messages.error(request, 'تداخل زمانی بین دوره‌های انتخابی')
            return redirect('home_view')
        
        for course in selected_courses:
            StudentCourse.objects.create(
                student=student,
                course=course,
                status='enrolled'
            )
            course.remaining_capacity -= 1
            course.save()
        
        request.session['selected_courses'] = []
        messages.success(request, 'ثبت‌نام با موفقیت انجام شد')
    
    return redirect('home_view')

def has_time_conflict(student, new_course):
    enrolled = StudentCourse.objects.filter(
        student=student, 
        status='enrolled'
    ).select_related('course')
    
    for course in enrolled:
        if check_time_overlap(new_course, course.course):
            return True
    return False

def check_time_overlap(course1, course2):
    days1 = set(course1.class_date.split(','))
    days2 = set(course2.class_date.split(','))
    
    common_days = days1.intersection(days2)
    if not common_days:
        return False
    
    def to_minutes(time_str):
        h, m = map(int, time_str.split(':'))
        return h * 60 + m
    
    start1, end1 = course1.class_time.split('-')
    start2, end2 = course2.class_time.split('-')
    
    start1_min = to_minutes(start1.strip())
    end1_min = to_minutes(end1.strip())
    start2_min = to_minutes(start2.strip())
    end2_min = to_minutes(end2.strip())
    
    return max(start1_min, start2_min) < min(end1_min, end2_min)

def has_time_conflict_in_list(courses):
    for i in range(len(courses)):
        for j in range(i+1, len(courses)):
            if check_time_overlap(courses[i], courses[j]):
                return True
    return False

def check_corequisites(course, student, session):
    pass

def sum_units(student, selected_ids):
    return Course.objects.filter(
        id__in=selected_ids
    ).aggregate(Sum('units'))['units__sum'] or 0



























@login_required
def student_view(request):
    DAY_MAPPING = {
        'Sat': 'شنبه',
        'Sun': 'یکشنبه',
        'Mon': 'دوشنبه',
        'Tue': 'سه شنبه',
        'Wed': 'چهارشنبه'
    }

    student = get_object_or_404(Student, user=request.user)
    student_courses = StudentCourse.objects.filter(student=student).select_related('course')

    persian_days = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه شنبه', 'چهارشنبه']
    time_slots = ['8:00-10:00', '10:00-12:00', '14:00-16:00', '16:00-18:00']
    
    schedule = {day: {time: [] for time in time_slots} for day in persian_days}

    for sc in student_courses:
        course = sc.course
        try:
            for english_day in course.class_date.split(','):
                english_day = english_day.strip()
                persian_day = DAY_MAPPING.get(english_day)
                
                if persian_day and persian_day in schedule:
                    if course.class_time in schedule[persian_day]:
                        schedule[persian_day][course.class_time].append({
                            'course_name': course.course_name,
                            'course_code': course.course_code,
                            'classroom': course.classroom,
                            'professor': course.professor
                        })
        except AttributeError:
            continue

    print(f"Loaded {student_courses.count()} courses for {student}")
    for day in persian_days:
        print(f"{day} schedule:")
        for time in time_slots:
            courses = schedule[day][time]
            if courses:
                print(f"  {time}: {[c['course_name'] for c in courses]}")

    context = {
        'student': student,
        'schedule': schedule,
        'days': persian_days,
        'time_slots': time_slots,
        'student_info': {
            'gpa': student.gpa,
            'current_units': student.get_current_units(),
            'max_units': student.max_units
        }
    }

    return render(request, 'student/schedule.html', context)





@login_required
def student_profile(request):
    student = get_object_or_404(Student, user=request.user)
    enrolled_courses = StudentCourse.objects.filter(
        student=student,
        status='enrolled'
    ).select_related('course')
    
    if request.method == 'POST':
        if 'profile_update' in request.POST:
            student.first_name = request.POST.get('first_name')
            student.last_name = request.POST.get('last_name')
            student.email = request.POST.get('email')
            student.phone_number = request.POST.get('phone_number')
            

            try:
                student.full_clean()
                student.save()
                messages.success(request, 'اطلاعات با موفقیت به روز رسانی شد')
            except ValidationError as e:
                messages.error(request, f'خطا در اعتبارسنجی: {e}')
        
        elif 'course_withdraw' in request.POST:
            course_id = request.POST.get('course_id')
            return withdraw_course(request, course_id)
    
    context = {
        'student': {
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': student.email,
            'phone_number': student.phone_number,
            'major': student.major.major_name,
            'gpa': student.gpa,
            'current_units': student.get_current_units(),
            'max_units': student.max_units
        },
        'courses': [
            {
                'id': sc.course.id,
                'name': sc.course.course_name,
                'code': sc.course.course_code,
                'units': sc.course.units,
                'professor': sc.course.professor.last_name,
                'remaining_capacity': sc.course.remaining_capacity
            } for sc in enrolled_courses
        ]
    }
    
    return render(request, 'student/profile.html', context)

@require_POST
@login_required
@transaction.atomic
def withdraw_course(request, course_id):
    student = get_object_or_404(Student, user=request.user)
    course = get_object_or_404(Course, pk=course_id)
    enrollment = get_object_or_404(
        StudentCourse,
        student=student,
        course=course,
        status='enrolled'
    )
    
    enrollment.status = 'withdrawn'
    enrollment.save()
    
    course.remaining_capacity += 1
    course.save()
    
    enrollment.delete()
    messages.success(request, f'دوره {course.course_name} با موفقیت حذف شد')
    return redirect('student_profile')


