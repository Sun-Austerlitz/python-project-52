from django.shortcuts import redirect
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Task
from .forms import TaskForm
from statuses.models import Status
from django.contrib.auth.models import User


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        queryset = super().get_queryset()

        # Фильтрация по статусу
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status_id=status)

        # Фильтрация по исполнителю
        executor = self.request.GET.get("executor")
        if executor:
            queryset = queryset.filter(executor_id=executor)

        # Фильтрация по метке (если метки добавлены в проект)
        label = self.request.GET.get("label")
        if label:
            queryset = queryset.filter(labels__id=label)

        # Фильтрация "Только свои задачи"
        if self.request.GET.get("self_tasks"):
            queryset = queryset.filter(author=self.request.user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = Status.objects.all()
        context["users"] = User.objects.filter(
            id__in=Task.objects.values_list("executor", flat=True).distinct()
        )
        # Добавьте метки, если они есть в вашем проекте
        context["labels"] = []  # Пример: Label.objects.all()
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("task_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Задача успешно создана")
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("task_list")

    def form_valid(self, form):
        messages.success(self.request, "Задача успешно изменена")
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("task_list")

    def test_func(self):
        # Только автор задачи может её удалить
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, "Вы не можете удалить эту задачу.")
        return redirect("task_list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(self.request, "Задача успешно удалена")
        return super().post(request, *args, **kwargs)


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"
