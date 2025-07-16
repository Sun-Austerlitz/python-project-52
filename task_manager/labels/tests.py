from django.test import TestCase
from django.urls import reverse
from task_manager.labels.models import Label
from task_manager.tasks.models import Task
from task_manager.statuses.models import Status
from django.contrib.auth.models import User


class LabelCRUDTests(TestCase):
    fixtures = ["users.json"]  # Загружаем фикстуру с пользователями

    def setUp(self):
        # Логинимся под существующим пользователем
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)
        self.status = Status.objects.create(name="In Progress")

    def test_label_list_view(self):
        """Тест отображения списка меток"""
        response = self.client.get(reverse("label_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "labels/label_list.html")

    def test_label_create_success(self):
        """Тест успешного создания метки"""
        response = self.client.post(
            reverse("label_create"),
            {"name": "New Label"},
        )
        self.assertEqual(
            response.status_code,
            302,
        )  # Перенаправление после создания
        self.assertTrue(Label.objects.filter(name="New Label").exists())

    def test_label_create_failure_duplicate_name(self):
        """Тест неуспешного создания метки с дублирующимся именем"""
        Label.objects.create(name="Duplicate Label")
        response = self.client.post(
            reverse("label_create"),
            {"name": "Duplicate Label"},
        )
        self.assertEqual(
            response.status_code,
            200,
        )  # Остаёмся на странице создания
        self.assertContains(
            response,
            "Label with this Имя already exists.",
        )
        self.assertEqual(
            Label.objects.filter(name="Duplicate Label").count(),
            1,
        )

    def test_label_update_success(self):
        """Тест успешного обновления метки"""
        label = Label.objects.create(name="Old Label")
        response = self.client.post(
            reverse("label_update", kwargs={"pk": label.pk}),
            {"name": "Updated Label"},
        )
        self.assertEqual(
            response.status_code,
            302,
        )  # Перенаправление после обновления
        label.refresh_from_db()
        self.assertEqual(label.name, "Updated Label")

    def test_label_update_failure_duplicate_name(self):
        """Тест неуспешного обновления метки с дублирующимся именем"""
        Label.objects.create(name="Existing Label")
        label = Label.objects.create(name="Old Label")
        response = self.client.post(
            reverse("label_update", kwargs={"pk": label.pk}),
            {"name": "Existing Label"},
        )
        self.assertEqual(
            response.status_code,
            200,
        )  # Остаёмся на странице обновления
        self.assertContains(response, "Label with this Имя already exists.")
        label.refresh_from_db()
        self.assertEqual(label.name, "Old Label")  # Имя не изменилось

    def test_label_delete_success(self):
        """Тест успешного удаления метки"""
        label = Label.objects.create(name="Temporary Label")
        response = self.client.post(
            reverse(
                "label_delete",
                kwargs={"pk": label.pk},
            )
        )
        self.assertEqual(
            response.status_code,
            302,
        )  # Перенаправление после удаления
        self.assertFalse(Label.objects.filter(pk=label.pk).exists())

    def test_label_delete_failure_with_tasks(self):
        """Тест неуспешного удаления метки, связанной с задачами"""
        label = Label.objects.create(name="Linked Label")
        task = Task.objects.create(
            name="Task with Label",
            description="Task description",
            status=self.status,
            author=self.user,
        )
        task.labels.add(label)  # Связываем метку с задачей
        response = self.client.post(
            reverse(
                "label_delete",
                kwargs={"pk": label.pk},
            )
        )
        self.assertEqual(
            response.status_code,
            302,
        )  # Перенаправление на список меток
        self.assertTrue(Label.objects.filter(pk=label.pk).exists())
        # Проверяем, что сообщение об ошибке отображается
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Невозможно удалить метку, так как она связана с задачами.",
        )
