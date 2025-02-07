from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm, StudentProfileForm
from django.contrib.auth.views import LogoutView, LoginView

class CustomLogoutView(LogoutView):
    next_page = 'login' 

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('create_student_profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def create_student_profile(request):
    if hasattr(request.user, 'student'):
        return redirect('home')
        
    if request.method == 'POST':
        form = StudentProfileForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.user = request.user
            student.save()
            return redirect('home_view')
    else:
        form = StudentProfileForm()
    
    return render(request, 'accounts/create_student_profile.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        super().form_valid(form)
        user = self.request.user
        
        if user.is_staff or user.is_superuser:
            return redirect('course_list_view')
        else:
            return redirect('home_view')
        
