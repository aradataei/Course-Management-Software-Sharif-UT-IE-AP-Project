from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Student,
    CustomUser,
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
            'first_name': 'نام ',
            'last_name': 'نام خانوادگی ',
            'major': 'رشته تحصیلی',
            'phone_number': 'شماره تلفن',
            'email': 'ایمیل',
            'admission_form': 'سال ورود',
        }


