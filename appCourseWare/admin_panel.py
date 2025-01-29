from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.views.generic.edit import FormMixin

from . import models
from . import forms


class AdminDashboardView(TemplateView):
    template_name = 'admin_panel/dashboard.html'


class CourseListView(ListView):
    model = models.Course
    template_name = 'admin_panel/course/list.html'
    context_object_name = 'courses'


class CourseCreateView(CreateView):
    model = models.Course
    form_class = forms.CourseForm
    template_name = 'admin_panel/course/create.html'
    success_url = reverse_lazy('admin_panel:course_list')


class CourseUpdateView(UpdateView):
    model = models.Course
    form_class = forms.CourseForm
    template_name = 'admin_panel/course/update.html'
    success_url = reverse_lazy('admin_panel:course_list')


class CourseDeleteView(DeleteView):
    model = models.Course
    template_name = 'admin_panel/course/delete.html'
    success_url = reverse_lazy('admin_panel:course_list')


class ProfessorListView(ListView):
    model = models.Professor
    template_name = 'admin_panel/professor/list.html'
    context_object_name = 'professors'


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


class ClassListView(ListView):
    model = models.Class
    template_name = 'admin_panel/class/list.html'
    context_object_name = 'classes'


class ClassCreateView(CreateView):
    model = models.Class
    form_class = forms.ClassForm
    template_name = 'admin_panel/class/create.html'
    success_url = reverse_lazy('admin_panel:class_list')


class ClassUpdateView(UpdateView):
    model = models.Class
    form_class = forms.ClassForm
    template_name = 'admin_panel/class/update.html'
    success_url = reverse_lazy('admin_panel:class_list')


class ClassDeleteView(DeleteView):
    model = models.Class
    template_name = 'admin_panel/class/delete.html'
    success_url = reverse_lazy('admin_panel:class_list')


class PrerequisiteListView(ListView):
    model = models.Prerequisite
    template_name = 'admin_panel/prerequisite/list.html'
    context_object_name = 'prerequisites'


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


class CorequisiteListView(ListView):
    model = models.Corequisite
    template_name = 'admin_panel/corequisite/list.html'
    context_object_name = 'corequisites'


class CorequisiteCreateView(CreateView):
    model = models.Corequisite
    form_class = forms.CorequisiteForm
    template_name = 'admin_panel/corequisite/create.html'
    success_url = reverse_lazy('admin_panel:corequisite_list')


class CorequisiteUpdateView(UpdateView):
    model = models.Corequisite
    form_class = forms.CorequisiteForm
    template_name = 'admin_panel/corequisite/update.html'
    success_url = reverse_lazy('admin_panel:corequisite_list')


class CorequisiteDeleteView(DeleteView):
    model = models.Corequisite
    template_name = 'admin_panel/corequisite/delete.html'
    success_url = reverse_lazy('admin_panel:corequisite_list')
