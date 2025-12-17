from datetime import timedelta

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import ProfileForm, RegisterForm, TaskForm
from .models import Category, Profile, Task


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("task_list")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "tasks/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username=username)

        if not hasattr(user, "profile"):
            Profile.objects.create(user=user)

        context["profile_user"] = user
        context["profile"] = user.profile
        context["is_own_profile"] = self.request.user == user

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)

        user_tasks = Task.objects.filter(assigned_to=user)

        def get_metrics(start_date):
            period_tasks = user_tasks.filter(created_at__gte=start_date)
            completed = period_tasks.filter(status="done").count()
            total = period_tasks.count()
            in_progress = period_tasks.filter(status="in_progress").count()
            hours = sum(
                t.estimated_hours or 0 for t in period_tasks.filter(status="done")
            )
            return {
                "completed": completed,
                "total": total,
                "in_progress": in_progress,
                "hours": hours,
                "completion_rate": round(completed / total * 100) if total > 0 else 0,
            }

        context["metrics_today"] = get_metrics(today_start)
        context["metrics_week"] = get_metrics(week_start)
        context["metrics_month"] = get_metrics(month_start)

        context["all_tasks"] = user_tasks.count()
        context["all_completed"] = user_tasks.filter(status="done").count()
        context["all_hours"] = sum(
            t.estimated_hours or 0 for t in user_tasks.filter(status="done")
        )

        context["recent_tasks"] = user_tasks.order_by("-created_at")[:5]

        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "tasks/profile_edit.html"

    def get_object(self):
        if not hasattr(self.request.user, "profile"):
            Profile.objects.create(user=self.request.user)
        return self.request.user.profile

    def get_success_url(self):
        return reverse_lazy("profile", kwargs={"username": self.request.user.username})


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = 10

    def get_queryset(self):
        queryset = Task.objects.select_related("category", "assigned_to")

        category_id = self.request.GET.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        priority = self.request.GET.get("priority")
        if priority:
            queryset = queryset.filter(priority=priority)

        date_filter = self.request.GET.get("date_filter")
        today = timezone.now().date()
        if date_filter == "today":
            queryset = queryset.filter(deadline__date=today)
        elif date_filter == "week":
            week_end = today + timedelta(days=7)
            queryset = queryset.filter(
                deadline__date__gte=today, deadline__date__lte=week_end
            )
        elif date_filter == "overdue":
            queryset = queryset.filter(deadline__lt=timezone.now()).exclude(
                status="done"
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["statuses"] = Task.STATUS_CHOICES
        context["priorities"] = Task.PRIORITY_CHOICES
        context["current_category"] = self.request.GET.get("category", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["current_priority"] = self.request.GET.get("priority", "")
        context["current_date_filter"] = self.request.GET.get("date_filter", "")
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("task_list")


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("task_list")


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("task_list")


class KanbanView(LoginRequiredMixin, TemplateView):
    template_name = "tasks/kanban.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = Task.STATUS_CHOICES
        context["tasks_by_status"] = {
            status[0]: Task.objects.filter(status=status[0]).select_related(
                "category", "assigned_to"
            )
            for status in Task.STATUS_CHOICES
        }
        return context


class UpdateTaskStatusView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = Task.objects.get(pk=pk)
        new_status = request.POST.get("status")
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "Invalid status"}, status=400)
