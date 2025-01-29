from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.forms import ValidationError
from . import models
from . import forms


# داشبورد ادمین
class AdminDashboardView(TemplateView):
    template_name = 'admin_panel/dashboard.html'


# لیست دوره‌ها با قابلیت جستجو و فیلتر
class CourseListView(ListView):
    model = models.Course
    template_name = 'admin_panel/course/list.html'
    context_object_name = 'courses'
    paginate_by = 10
    ordering = ['course_name']
    # افزودن فیلترها و قابلیت جستجو
    # برای این منظور نیاز به تعریف SearchFilter یا استفاده از کتابخانه‌های جانبی دارید


class CourseCreateView(CreateView):
    model = models.Course
    form_class = forms.CourseForm
    template_name = 'admin_panel/course/create.html'
    success_url = reverse_lazy('admin_panel:course_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # افزودن منطق اضافی در صورت نیاز
        return response


class CourseUpdateView(UpdateView):
    model = models.Course
    form_class = forms.CourseForm
    template_name = 'admin_panel/course/update.html'
    success_url = reverse_lazy('admin_panel:course_list')


class CourseDeleteView(DeleteView):
    model = models.Course
    template_name = 'admin_panel/course/delete.html'
    success_url = reverse_lazy('admin_panel:course_list')


# مدیریت پروفسورها با قابلیت جستجو
class ProfessorListView(ListView):
    model = models.Professor
    template_name = 'admin_panel/professor/list.html'
    context_object_name = 'professors'
    paginate_by = 10
    ordering = ['last_name', 'first_name']


class ProfessorCreateView(CreateView):
    model = models.Professor
    form_class = forms.ProfessorForm
    template_name = 'admin_panel/professor/create.html'
    success_url = reverse_lazy('admin_panel:professor_list')


class ProfessorUpdateView(UpdateView):
    model = models.Professor
    form_class = forms.ProfessorForm
    template_name = 'admin_panel/professor/update.html'
    success_url = reverse_lazy('admin_panel:professor_list')


class ProfessorDeleteView(DeleteView):
    model = models.Professor
    template_name = 'admin_panel/professor/delete.html'
    success_url = reverse_lazy('admin_panel:professor_list')


# مدیریت کلاس‌ها
class ClassListView(ListView):
    model = models.Classroom
    template_name = 'admin_panel/classroom/list.html'
    context_object_name = 'classrooms'
    paginate_by = 10
    ordering = ['clssroom_name', 'department']


class ClassCreateView(CreateView):
    model = models.Classroom
    form_class = forms.ClassForm
    template_name = 'admin_panel/classroom/create.html'
    success_url = reverse_lazy('admin_panel:class_list')


class ClassUpdateView(UpdateView):
    model = models.Classroom
    form_class = forms.ClassForm
    template_name = 'admin_panel/classroom/update.html'
    success_url = reverse_lazy('admin_panel:class_list')


class ClassDeleteView(DeleteView):
    model = models.Classroom
    template_name = 'admin_panel/classroom/delete.html'
    success_url = reverse_lazy('admin_panel:class_list')


# مدیریت پیش نیازها
class PrerequisiteListView(ListView):
    model = models.Prerequisite
    template_name = 'admin_panel/prerequisite/list.html'
    context_object_name = 'prerequisites'
    paginate_by = 10
    ordering = ['course__course_name']


class PrerequisiteCreateView(CreateView):
    model = models.Prerequisite
    form_class = forms.PrerequisiteForm
    template_name = 'admin_panel/prerequisite/create.html'
    success_url = reverse_lazy('admin_panel:prerequisite_list')


class PrerequisiteUpdateView(UpdateView):
    model = models.Prerequisite
    form_class = forms.PrerequisiteForm
    template_name = 'admin_panel/prerequisite/update.html'
    success_url = reverse_lazy('admin_panel:prerequisite_list')


class PrerequisiteDeleteView(DeleteView):
    model = models.Prerequisite
    template_name = 'admin_panel/prerequisite/delete.html'
    success_url = reverse_lazy('admin_panel:prerequisite_list')


# مدیریت هم نیازها
class CoRequisiteListView(ListView):
    model = models.CoRequisite
    template_name = 'admin_panel/corequisite/list.html'
    context_object_name = 'corequisites'
    paginate_by = 10
    ordering = ['course__course_name']


class CoRequisiteCreateView(CreateView):
    model = models.CoRequisite
    form_class = forms.CorequisiteForm
    template_name = 'admin_panel/corequisite/create.html'
    success_url = reverse_lazy('admin_panel:corequisite_list')


class CoRequisiteUpdateView(UpdateView):
    model = models.CoRequisite
    form_class = forms.CorequisiteForm
    template_name = 'admin_panel/corequisite/update.html'
    success_url = reverse_lazy('admin_panel:corequisite_list')


class CoRequisiteDeleteView(DeleteView):
    model = models.CoRequisite
    template_name = 'admin_panel/corequisite/delete.html'
    success_url = reverse_lazy('admin_panel:corequisite_list')
