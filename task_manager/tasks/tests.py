from django.test import TestCase
from django.urls import reverse
from task_manager.tasks.models import Task
from task_manager.statuses.models import Status
from task_manager.labels.models import Label
from django.contrib.auth.models import User


class TaskCRUDTests(TestCase):
    fixtures = ["users.json"]  # Загружаем фикстуру с пользователями

    def setUp(self):
        # Логинимся под существующим пользователем
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)
        self.status = Status.objects.create(name="In Progress")
        self.label = Label.objects.create(name="Bug")

    def test_task_list_view(self):
        """Тест отображения списка задач"""
        response = self.client.get(reverse("task_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/task_list.html")

    def test_task_create_success(self):
        """Тест успешного создания задачи"""
        response = self.client.post(
            reverse("task_create"),
            {
                "name": "New Task",
                "description": "Task description",
                "status": self.status.pk,
                "executor": "",
                "labels": [self.label.pk],
            },
        )
        self.assertEqual(
            response.status_code,
            302,
        )  # Перенаправление после создания
        self.assertTrue(Task.objects.filter(name="New Task").exists())

    def test_task_update_success(self):
        """Тест успешного обновления задачи"""
        task = Task.objects.create(
            name="Old Task",
            description="Old description",
            status=self.status,
            author=self.user,
        )
        response = self.client.post(
            reverse("task_update", kwargs={"pk": task.pk}),
            {
                "name": "Updated Task",
                "description": "Updated description",
                "status": self.status.pk,
                "executor": "",
                "labels": [self.label.pk],
            },
        )
        self.assertEqual(
            response.status_code,
            302,
        )  # Перенаправление после обновления
        task.refresh_from_db()
        self.assertEqual(task.name, "Updated Task")
        self.assertEqual(task.description, "Updated description")

    def test_task_delete_success(self):
        """Тест успешного удаления задачи"""
        task = Task.objects.create(
            name="Task to delete",
            description="Task description",
            status=self.status,
            author=self.user,
        )
        response = self.client.post(
            reverse(
                "task_delete",
                kwargs={"pk": task.pk},
            )
        )
        self.assertEqual(
            response.status_code,
            302,
        )  # Перенаправление после удаления
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_task_delete_failure_not_author(self):
        """Тест неуспешного удаления задачи другим пользователем"""
        other_user = User.objects.create_user(
            username="otheruser", password="password123"
        )
        task = Task.objects.create(
            name="Task to delete",
            description="Task description",
            status=self.status,
            author=self.user,
        )
        self.client.force_login(
            other_user,
        )  # Логинимся как другой пользователь
        response = self.client.post(
            reverse(
                "task_delete",
                kwargs={"pk": task.pk},
            )
        )
        self.assertEqual(
            response.status_code,
            302,
        )  # Перенаправление на список задач
        self.assertTrue(
            Task.objects.filter(
                pk=task.pk,
            ).exists()
        )  # Задача не удалена
        # Проверяем, что сообщение об ошибке отображается
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Задачу может удалить только ее автор",
        )

    def test_task_detail_view(self):
        """Тест отображения деталей задачи"""
        task = Task.objects.create(
            name="Task Detail",
            description="Task description",
            status=self.status,
            author=self.user,
        )
        response = self.client.get(
            reverse(
                "task_detail",
                kwargs={"pk": task.pk},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/task_detail.html")
        self.assertContains(response, "Task Detail")
        self.assertContains(response, "Task description")
