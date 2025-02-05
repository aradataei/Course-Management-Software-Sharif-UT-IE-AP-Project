from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required
from .models import Course, Department, Student, StudentCourse, Prerequisite

@login_required
def home_view(request):
    
    student = Student.objects.get(user=request.user)
    session = request.session
    
    # مدیریت سشن برای دوره‌های انتخابی موقت
    if 'selected_courses' not in session:
        session['selected_courses'] = []
        session.modified = True
    
    # پردازش درخواست‌های POST
    if request.method == 'POST':
        # افزودن دوره جدید
        if 'add_course' in request.POST:
            course_id = request.POST.get('course_id')
            return handle_add_course(request, course_id, student)
        
        # حذف دوره از سبد
        if 'remove_course' in request.POST:
            course_id = request.POST.get('course_id')
            return handle_remove_course(request, course_id)
        
        # ثبت نهایی دوره‌ها
        if 'finalize' in request.POST:
            return handle_finalize(request, student)
    
    # فیلتر کردن دوره‌ها
    courses = filter_courses(request)
    
    # محاسبه واحدها
    current_units = StudentCourse.objects.filter(
        student=student, 
        status='enrolled'
    ).aggregate(Sum('course__units'))['course__units__sum'] or 0
    
    selected_units = Course.objects.filter(
        id__in=session['selected_courses']
    ).aggregate(Sum('units'))['units__sum'] or 0
    
    # آماده سازی داده برای تمپلیت
    context = {
        'courses': courses.prefetch_related('prerequisites'),
        'departments': Department.objects.all(),
        'current_units': current_units,
        'selected_units': selected_units,
        'max_units': student.max_units,
        'remaining_units': student.max_units - (current_units + selected_units),
        'selected_courses': Course.objects.filter(id__in=session['selected_courses']),
        'enrolled_courses': StudentCourse.objects.filter(student=student, status='enrolled')
    }
    
    return render(request, 'student/home.html', context)

# ---------- توابع کمکی ----------

def filter_courses(request):
    """فیلتر کردن دوره‌ها بر اساس پارامترهای جستجو"""
    courses = Course.objects.filter(remaining_capacity__gt=0)
    
    # فیلتر دپارتمان
    department = request.GET.get('department')
    if department and department != 'all':
        courses = courses.filter(department__name=department)
    
    # جستجو بر اساس کد یا نام درس
    search = request.GET.get('search')
    if search:
        courses = courses.filter(
            Q(course_code__icontains=search) |
            Q(course_name__icontains=search)
        )
    
    return courses

def handle_add_course(request, course_id, student):
    """مدیریت منطق افزودن دوره"""
    course = get_object_or_404(Course, pk=course_id)
    session = request.session
    
    # بررسی تداخل زمانی
    if has_time_conflict(student, course):
        messages.error(request, f'تداخل زمانی با {course.course_name}')
        return redirect('home_view')
    
    # بررسی پیشنیازها
    if not check_prerequisites(student, course):
        messages.error(request, f'پیشنیازهای {course.course_name} تکمیل نشده')
        return redirect('home_view')
    
    # بررسی تعداد واحدها
    new_units = sum_units(student, session['selected_courses']) + course.units
    if new_units > student.max_units:
        messages.error(request, 'تعداد واحد مجاز превыشده')
        return redirect('home_view')
    
    # افزودن به سشن
    if course_id not in session['selected_courses']:
        session['selected_courses'].append(course_id)
        session.modified = True
        messages.success(request, f'{course.course_name} به سبد اضافه شد')
    
    return redirect('home_view')

def handle_remove_course(request, course_id):
    """مدیریت حذف دوره از سبد"""
    session = request.session
    if course_id in session['selected_courses']:
        session['selected_courses'].remove(course_id)
        session.modified = True
        messages.success(request, 'دوره با موفقیت حذف شد')
    return redirect('home_view')

def handle_finalize(request, student):
    """ثبت نهایی دوره‌ها"""
    with transaction.atomic():
        selected_courses = Course.objects.filter(
            id__in=request.session['selected_courses']
        )
        
        # بررسی نهایی تداخل زمانی
        if has_time_conflict_in_list(selected_courses):
            messages.error(request, 'تداخل زمانی بین دوره‌های انتخابی')
            return redirect('home_view')
        
        # ایجاد رکوردهای ثبت‌نام
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

# ---------- توابع بررسی ----------

def has_time_conflict(student, new_course):
    """بررسی تداخل زمانی با دوره‌های ثبت‌نام شده"""
    enrolled = StudentCourse.objects.filter(
        student=student, 
        status='enrolled'
    ).select_related('course')
    
    for course in enrolled:
        if check_time_overlap(new_course, course.course):
            return True
    return False

def check_time_overlap(course1, course2):
    """بررسی تداخل زمانی بین دو دوره"""
    # تبدیل روزهای برگزاری به مجموعه
    days1 = set(course1.class_date.split(','))
    days2 = set(course2.class_date.split(','))
    
    # بررسی تداخل روزهای برگزاری
    common_days = days1.intersection(days2)
    if not common_days:
        return False
    
    # تبدیل زمان به دقیقه
    def to_minutes(time_str):
        h, m = map(int, time_str.split(':'))
        return h * 60 + m
    
    # استخراج زمان شروع و پایان
    start1, end1 = course1.class_time.split('-')
    start2, end2 = course2.class_time.split('-')
    
    # محاسبه دقیقه
    start1_min = to_minutes(start1.strip())
    end1_min = to_minutes(end1.strip())
    start2_min = to_minutes(start2.strip())
    end2_min = to_minutes(end2.strip())
    
    # بررسی تداخل زمانی
    return max(start1_min, start2_min) < min(end1_min, end2_min)

def has_time_conflict_in_list(courses):
    """بررسی تداخل زمانی بین لیست دوره‌ها"""
    for i in range(len(courses)):
        for j in range(i+1, len(courses)):
            if check_time_overlap(courses[i], courses[j]):
                return True
    return False

def check_prerequisites(student, course):
    """بررسی پیشنیازهای دوره"""
    required = course.prerequisites.all()
    completed = StudentCourse.objects.filter(
        student=student,
        status='completed'
    ).values_list('course__id', flat=True)
    
    return all(req.id in completed for req in required)

def sum_units(student, selected_ids):
    """محاسبه مجموع واحدهای انتخابی"""
    return Course.objects.filter(
        id__in=selected_ids
    ).aggregate(Sum('units'))['units__sum'] or 0