from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from .models import Status
from .forms import StatusForm


class StatusListView(LoginRequiredMixin, ListView):
    model = Status
    template_name = "statuses/status_list.html"
    context_object_name = "statuses"


class StatusCreateView(LoginRequiredMixin, CreateView):
    model = Status
    form_class = StatusForm
    template_name = "statuses/status_form.html"
    success_url = reverse_lazy("status_list")

    def form_valid(self, form):
        messages.success(self.request, "Статус успешно создан.")
        return super().form_valid(form)


class StatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Status
    form_class = StatusForm
    template_name = "statuses/status_form.html"
    success_url = reverse_lazy("status_list")

    def handle_no_permission(self):
        # Вывод сообщения и перенаправление на страницу входа
        messages.error(
            self.request,
            "Вы не авторизованы! Пожалуйста, выполните вход.",
        )
        return redirect(reverse("login"))

    def form_valid(self, form):
        messages.success(self.request, "Статус успешно изменен")
        return super().form_valid(form)


class StatusDeleteView(LoginRequiredMixin, DeleteView):
    model = Status
    template_name = "statuses/status_confirm_delete.html"
    success_url = reverse_lazy("status_list")

    def handle_no_permission(self):
        # Вывод сообщения и перенаправление на страницу входа
        messages.error(
            self.request,
            "Вы не авторизованы! Пожалуйста, выполните вход.",
        )
        return redirect(reverse("login"))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Проверяем, связаны ли задачи с этим статусом
        if hasattr(self.object, "task_set") and self.object.task_set.exists():
            messages.error(
                self.request,
                "Невозможно удалить статус, так как он связан с задачами.",
            )
            return redirect("status_list")
        messages.success(self.request, "Статус успешно удален.")
        return super().post(request, *args, **kwargs)
