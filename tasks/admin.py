from django.contrib import admin

from .models import Category, Task, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at"]
    search_fields = ["user__username", "bio"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "category",
        "assigned_to",
        "priority",
        "status",
        "estimated_hours",
        "deadline",
        "created_at",
    ]
    list_filter = [
        "status",
        "priority",
        "category",
        "assigned_to",
        "created_at",
        "deadline",
    ]
    search_fields = ["title", "description"]
    list_editable = ["status", "priority", "estimated_hours"]
    filter_horizontal = ["blocked_by"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
