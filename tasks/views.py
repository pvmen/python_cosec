from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views import View
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta
from .models import Task, Category
from .forms import TaskForm, RegisterForm


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10

    def get_queryset(self):
        queryset = Task.objects.select_related('category', 'assigned_to')

        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        date_filter = self.request.GET.get('date_filter')
        today = timezone.now().date()
        if date_filter == 'today':
            queryset = queryset.filter(deadline__date=today)
        elif date_filter == 'week':
            week_end = today + timedelta(days=7)
            queryset = queryset.filter(deadline__date__gte=today, deadline__date__lte=week_end)
        elif date_filter == 'overdue':
            queryset = queryset.filter(deadline__lt=timezone.now()).exclude(status='done')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['statuses'] = Task.STATUS_CHOICES
        context['priorities'] = Task.PRIORITY_CHOICES
        context['current_category'] = self.request.GET.get('category', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_priority'] = self.request.GET.get('priority', '')
        context['current_date_filter'] = self.request.GET.get('date_filter', '')
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')


class KanbanView(LoginRequiredMixin, TemplateView):
    template_name = 'tasks/kanban.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Task.STATUS_CHOICES
        context['tasks_by_status'] = {
            status[0]: Task.objects.filter(status=status[0]).select_related('category', 'assigned_to')
            for status in Task.STATUS_CHOICES
        }
        return context


class UpdateTaskStatusView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = Task.objects.get(pk=pk)
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
