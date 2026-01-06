from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import ProjectForm, TaskForm, CommentForm
from .models import Project, Task, Comment


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "tracker/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        projects = Project.objects.filter(owner=self.request.user)
        tasks = Task.objects.filter(project__owner=self.request.user)

        stats = tasks.values("status").annotate(total=Count("id"))
        stat_map = {s["status"]: s["total"] for s in stats}

        ctx["projects_count"] = projects.count()
        ctx["tasks_total"] = tasks.count()
        ctx["tasks_todo"] = stat_map.get(Task.Status.TODO, 0)
        ctx["tasks_in_progress"] = stat_map.get(Task.Status.IN_PROGRESS, 0)
        ctx["tasks_done"] = stat_map.get(Task.Status.DONE, 0)

        ctx["recent_tasks"] = tasks.select_related("project")[:8]
        return ctx


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "tracker/project_list.html"
    context_object_name = "projects"
    paginate_by = 8

    def get_queryset(self):
        qs = Project.objects.filter(owner=self.request.user)
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        return qs


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "tracker/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        project = self.object

        status = self.request.GET.get("status", "")
        priority = self.request.GET.get("priority", "")
        q = self.request.GET.get("q", "").strip()

        tasks = project.tasks.prefetch_related("labels").all()
        if q:
            tasks = tasks.filter(Q(title__icontains=q) | Q(description__icontains=q))
        if status in {Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.DONE}:
            tasks = tasks.filter(status=status)
        if priority in {"1", "2", "3"}:
            tasks = tasks.filter(priority=int(priority))

        ctx["tasks"] = tasks
        ctx["comment_form"] = CommentForm()
        return ctx


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "tracker/project_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Проєкт створено ✅")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("project_detail", kwargs={"pk": self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "tracker/project_form.html"

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Зміни збережено ✅")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("project_detail", kwargs={"pk": self.object.pk})


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = "tracker/confirm_delete.html"
    success_url = reverse_lazy("project_list")

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = "tracker/task_form.html"
    form_class = TaskForm

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=kwargs["project_id"], owner=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["owner"] = self.request.user
        return kw

    def form_valid(self, form):
        form.instance.project = self.project
        messages.success(self.request, "Задачу створено ✅")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("project_detail", kwargs={"pk": self.project.pk})


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = "tracker/task_form.html"
    form_class = TaskForm

    def get_queryset(self):
        return Task.objects.filter(project__owner=self.request.user).select_related("project")

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["owner"] = self.request.user
        return kw

    def get_success_url(self):
        return reverse("project_detail", kwargs={"pk": self.object.project.pk})


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "tracker/confirm_delete.html"

    def get_queryset(self):
        return Task.objects.filter(project__owner=self.request.user).select_related("project")

    def get_success_url(self):
        return reverse("project_detail", kwargs={"pk": self.object.project.pk})


def _render_board(request: HttpRequest, project: Project) -> HttpResponse:
    tasks = project.tasks.prefetch_related("labels").all()
    return render(request, "tracker/partials/board.html", {"project": project, "tasks": tasks})


@login_required
def task_set_status(request: HttpRequest, task_id: int) -> HttpResponse:
    if request.method != "POST":
        return redirect("dashboard")

    task = get_object_or_404(Task, pk=task_id, project__owner=request.user)
    new_status = request.POST.get("status", "")
    if new_status not in {Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.DONE}:
        return _render_board(request, task.project)

    task.status = new_status
    task.save(update_fields=["status", "updated_at"])
    return _render_board(request, task.project)


@login_required
def comment_create(request: HttpRequest, task_id: int) -> HttpResponse:
    if request.method != "POST":
        return redirect("dashboard")

    task = get_object_or_404(Task, pk=task_id, project__owner=request.user)
    form = CommentForm(request.POST)
    if form.is_valid():
        Comment.objects.create(task=task, author=request.user, body=form.cleaned_data["body"])

    comments = task.comments.select_related("author").all()
    return render(request, "tracker/partials/comment_list.html", {"task": task, "comments": comments, "form": CommentForm()})
