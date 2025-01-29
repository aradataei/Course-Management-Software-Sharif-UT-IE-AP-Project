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
            user = form.save()
            login(request, user)
            # به جای ایجاد مستقیم Student، کاربر را به صفحه ایجاد Student هدایت می‌کنیم
            return redirect('create_student_profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# تابع جدید برای ایجاد پروفایل Student
def create_student_profile(request):
    # اگر کاربر قبلاً Student داشته باشد، به صفحه اصلی هدایت می‌شود
    if hasattr(request.user, 'student'):
        return redirect('home')
        
    if request.method == 'POST':
        form = StudentProfileForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.user = request.user
            student.save()
            return redirect('home')
    else:
        form = StudentProfileForm()
    
    return render(request, 'accounts/create_student_profile.html', {'form': form})
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        return super().form_valid(form)
    

