from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import CreateView, UpdateView
from .forms import CustomUserCreationForm, StudentProfileForm
from .models import Student, CustomUser
from django.contrib.auth.views import LogoutView, LoginView


class CustomLogoutView(LogoutView):
    next_page = 'login' 


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['student_id']
            
            # ذخیره اطلاعات اضافی اگر وجود داشته باشد
            if 'email' in request.POST:
                user.email = request.POST['email']
            if 'first_name' in request.POST:
                user.first_name = request.POST['first_name']
            if 'last_name' in request.POST:
                user.last_name = request.POST['last_name']
            
            user.save()
            
            # ایجاد پروفایل دانشجویی
            Student.objects.create(user=user)
            
            login(request, user)
            return redirect('complete-profile')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

class CompleteProfileView(UpdateView):
    model = Student
    form_class = StudentProfileForm
    template_name = 'accounts/complete_profile.html'
    success_url = '/dashboard/'
    
    def get_object(self):
        return self.request.user.student
    

from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        return super().form_valid(form)