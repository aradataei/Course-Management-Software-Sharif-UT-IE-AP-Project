from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Student,
    CustomUser,
    Course,
    Professor,
    Classroom,
    Prerequisite,
    CoRequisite,
)

class CustomUserCreationForm(UserCreationForm):
    student_id = forms.CharField(
        label="شماره دانشجویی",
        max_length=20,
        help_text="شماره دانشجویی خود را وارد کنید"
    )
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['student_id', 'password1', 'password2']

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['user']
        labels = {
            'entry_year': 'سال ورود',
            'entry_term': 'ترم ورود',
            'major': 'رشته تحصیلی',
            'supervisor': 'استاد راهنما',
            'military_status': 'وضعیت نظام وظیفه',
            'marital_status': 'وضعیت تاهل'
        }


class CourseForm(forms.ModelForm):
    prerequisites = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="پیش نیازها"
    )
    corequisites = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="هم نیازها"
    )

    class Meta:
        model = Course
        fields = [
            'course_name',
            'course_code',
            'exam_time',
            'capacity',
            'department',
            'professor',
            'classroom',
            'prerequisites',
            'corequisites',
            'class_date',
            'class_time'
        ]
        widgets = {
            'exam_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'class_date': forms.DateInput(attrs={'type': 'date'}),
            'class_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ['first_name', 'last_name', 'email', 'department']


class ClassForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['classroom_name', 'department']


class PrerequisiteForm(forms.ModelForm):
    class Meta:
        model = Prerequisite
        fields = ['course', 'required_course']


class CorequisiteForm(forms.ModelForm):
    class Meta:
        model = CoRequisite
        fields = ['course', 'required_course']