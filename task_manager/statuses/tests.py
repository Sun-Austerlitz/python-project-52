from django.test import TestCase
from django.urls import reverse
from task_manager.statuses.models import Status
from task_manager.tasks.models import Task
from django.contrib.auth.models import User


class StatusCRUDTests(TestCase):
    fixtures = ["users.json"]  # Загружаем фикстуру с пользователями

    def setUp(self):
        # Логинимся под существующим пользователем
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)

    def test_status_list_view(self):
        """Тест отображения списка статусов"""
        response = self.client.get(reverse("status_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "statuses/status_list.html")

    def test_status_create_success(self):
        """Тест успешного создания статуса"""
        response = self.client.post(
            reverse("status_create"),
            {"name": "New Status"},
        )
        self.assertEqual(
            response.status_code,
            302,
        )  # Перенаправление после создания
        self.assertTrue(Status.objects.filter(name="New Status").exists())

    def test_status_create_failure_duplicate_name(self):
        """Тест неуспешного создания статуса с дублирующимся именем"""
        Status.objects.create(name="Duplicate Status")
        response = self.client.post(
            reverse("status_create"),
            {"name": "Duplicate Status"},
        )
        self.assertEqual(
            response.status_code,
            200,
        )  # Остаёмся на странице создания
        self.assertContains(
            response,
            "Status with this Название already exists.",
        )
        self.assertEqual(
            Status.objects.filter(name="Duplicate Status").count(),
            1,
        )

    def test_status_update_success(self):
        """Тест успешного обновления статуса"""
        status = Status.objects.create(name="Old Status")
        response = self.client.post(
            reverse("status_update", kwargs={"pk": status.pk}),
            {"name": "Updated Status"},
        )
        self.assertEqual(
            response.status_code,
            302,
        )  # Перенаправление после обновления
        status.refresh_from_db()
        self.assertEqual(status.name, "Updated Status")

    def test_status_update_failure_duplicate_name(self):
        """Тест неуспешного обновления статуса с дублирующимся именем"""
        Status.objects.create(name="Existing Status")
        status = Status.objects.create(name="Old Status")
        response = self.client.post(
            reverse("status_update", kwargs={"pk": status.pk}),
            {"name": "Existing Status"},
        )
        self.assertEqual(
            response.status_code,
            200,
        )  # Остаёмся на странице обновления
        self.assertContains(
            response,
            "Status with this Название already exists.",
        )
        status.refresh_from_db()
        self.assertEqual(status.name, "Old Status")  # Имя не изменилось

    def test_status_delete_success(self):
        """Тест успешного удаления статуса"""
        status = Status.objects.create(name="Temporary Status")
        response = self.client.post(
            reverse(
                "status_delete",
                kwargs={"pk": status.pk},
            )
        )
        self.assertEqual(
            response.status_code,
            302,
        )  # Перенаправление после удаления
        self.assertFalse(Status.objects.filter(pk=status.pk).exists())

    def test_status_delete_failure_with_tasks(self):
        """Тест неуспешного удаления статуса, связанного с задачами"""
        status = Status.objects.create(name="Linked Status")
        # Создаём задачу, связанную с этим статусом
        Task.objects.create(name="Test Task", status=status, author=self.user)
        response = self.client.post(
            reverse(
                "status_delete",
                kwargs={"pk": status.pk},
            )
        )
        self.assertEqual(
            response.status_code, 302
        )  # Перенаправление на список статусов
        self.assertTrue(Status.objects.filter(pk=status.pk).exists())
        # Проверяем, что сообщение об ошибке отображается
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Невозможно удалить статус, так как он связан с задачами.",
        )
