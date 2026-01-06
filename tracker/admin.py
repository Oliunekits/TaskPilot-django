from django.contrib import admin
from .models import Project, Task, Label, Comment

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")
    search_fields = ("name", "owner__username")

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "priority", "due_date", "updated_at")
    list_filter = ("status", "priority")
    search_fields = ("title", "project__name")

@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "color")
    search_fields = ("name", "owner__username")

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("task", "author", "created_at")
    search_fields = ("task__title", "author__username", "body")
