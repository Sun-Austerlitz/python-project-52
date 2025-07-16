from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect


class CustomLoginView(LoginView):
    def form_valid(self, form):
        messages.success(self.request, "Вы залогинены")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Пожалуйста, введите правильные имя пользователя и пароль. "
            "Оба поля могут быть чувствительны к регистру.",
        )
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "Вы разлогинены")
        return super().dispatch(request, *args, **kwargs)


class UserListView(ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"


class UserCreateView(CreateView):
    model = User
    template_name = "users/user_form.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")

    def form_invalid(self, form):
        print(form.errors)  # Вывод ошибок формы в консоль
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "Пользователь успешно зарегистрирован")
        return super().form_valid(form)


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    template_name = "users/user_update_form.html"
    fields = ["first_name", "last_name", "username"]
    success_url = reverse_lazy("user_list")

    def test_func(self):
        # Проверяем, что пользователь пытается изменить только свои данные
        return self.get_object() == self.request.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.error(
                self.request, "Вы не авторизованы! Пожалуйста, выполните вход."
            )
            return HttpResponseRedirect(reverse("login"))
        else:
            messages.error(
                self.request,
                "У вас нет прав для изменения другого пользователя.",
            )
            return HttpResponseRedirect(reverse("user_list"))

    def form_valid(self, form):
        messages.success(self.request, "Пользователь успешно изменен.")
        return super().form_valid(form)


class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = "users/user_confirm_delete.html"
    success_url = reverse_lazy("user_list")

    def test_func(self):
        # Проверяем, что пользователь пытается удалить только свои данные
        return self.get_object() == self.request.user

    def handle_no_permission(self):
        # Если пользователь не авторизован, перенаправляем на страницу логина
        if not self.request.user.is_authenticated:
            messages.error(
                self.request, "Вы не авторизованы! Пожалуйста, выполните вход."
            )
            return redirect("login")
        # Если пользователь пытается удалить другого пользователя
        messages.error(
            self.request, "У вас нет прав для изменения другого пользователя."
        )
        return redirect("user_list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Проверяем, что пользователь действительно удаляет свои данные
        if self.object != request.user:
            messages.error(
                self.request,
                "У вас нет прав для изменения другого пользователя.",
            )
            return redirect("user_list")
        messages.success(self.request, "Пользователь успешно удален.")
        return super().post(request, *args, **kwargs)
