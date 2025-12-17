from django.contrib import admin
from .models import Category, Task


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'assigned_to', 'deadline', 'is_completed', 'created_at']
    list_filter = ['is_completed', 'category', 'assigned_to', 'created_at', 'deadline']
    search_fields = ['title', 'description']
    list_editable = ['is_completed']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
