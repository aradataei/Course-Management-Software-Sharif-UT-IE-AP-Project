from django import forms
from .models import Enrollment

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'status']
    
    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        status = cleaned_data.get('status')
        
        if status == 'enrolled':
            if course.remaining_capacity is not None and course.remaining_capacity <= 0:
                raise forms.ValidationError("Cannot enroll: course capacity has been reached.")
        
        return cleaned_data
