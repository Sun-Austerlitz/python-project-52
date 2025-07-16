from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class UserCRUDTests(TestCase):
    fixtures = ["users.json"]  # фикстура для загрузки данных

    def test_registration_success(self):
        """Тест успешной регистрации нового пользователя"""
        response = self.client.post(
            reverse("user_create"),
            {
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "password1": "password123",
                "password2": "password123",
            },
        )
        self.assertEqual(
            response.status_code, 302
        )  # Перенаправление после успешной регистрации
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_registration_failure_password_mismatch(self):
        """Тест неуспешной регистрации из-за несовпадения паролей"""
        response = self.client.post(
            reverse("user_create"),
            {
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "password1": "password123",
                "password2": "password456",
            },
        )
        # Остаёмся на странице регистрации
        self.assertEqual(response.status_code, 200)

        self.assertFalse(User.objects.filter(username="newuser").exists())

        # Проверяем сообщение об ошибке
        self.assertContains(
            response,
            "The two password fields didn’t match.",
        )

    def test_registration_failure_short_password(self):
        """Тест неуспешной регистрации из-за слишком короткого пароля"""
        response = self.client.post(
            reverse("user_create"),
            {
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "password1": "pw",
                "password2": "pw",
            },
        )
        # Остаёмся на странице регистрации
        self.assertEqual(response.status_code, 200)

        # Убедимся, что пользователь не создан
        self.assertFalse(User.objects.filter(username="newuser").exists())

        # Проверяем сообщение об ошибке
        self.assertContains(
            response,
            "Ваш пароль должен содержать как минимум 3 символа.",
        )

    def test_update_user_success(self):
        """Тест успешного обновления данных пользователя"""
        # Логинимся как существующий пользователь
        self.client.force_login(User.objects.get(pk=1))
        response = self.client.post(
            reverse("user_update", kwargs={"pk": 1}),
            {
                "username": "updateduser",
                "first_name": "Updated",
                "last_name": "User",
            },
        )
        self.assertEqual(
            response.status_code, 302
        )  # Перенаправление после успешного обновления
        user = User.objects.get(pk=1)
        self.assertEqual(user.username, "updateduser")
        self.assertEqual(user.first_name, "Updated")
        self.assertEqual(user.last_name, "User")

    def test_update_user_failure_not_logged_in(self):
        """Тест неуспешного обновления данных пользователя без авторизации"""
        # Получаем исходные данные пользователя
        user = User.objects.get(pk=1)
        original_username = user.username
        original_first_name = user.first_name
        original_last_name = user.last_name

        # Пытаемся обновить данные без авторизации
        response = self.client.post(
            reverse("user_update", kwargs={"pk": 1}),
            {
                "username": "updateduser",
                "first_name": "Updated",
                "last_name": "User",
            },
        )
        self.assertEqual(
            response.status_code, 302
        )  # Перенаправление на страницу логина

        # Проверяем, что данные пользователя не изменились
        user.refresh_from_db()  # Обновляем объект из базы данных
        self.assertEqual(user.username, original_username)
        self.assertEqual(user.first_name, original_first_name)
        self.assertEqual(user.last_name, original_last_name)

    def test_delete_user_success(self):
        """Тест успешного удаления пользователя"""
        # Логинимся как существующий пользователь
        self.client.force_login(User.objects.get(pk=1))
        response = self.client.post(reverse("user_delete", kwargs={"pk": 1}))
        self.assertEqual(
            response.status_code, 302
        )  # Перенаправление после успешного удаления
        self.assertFalse(User.objects.filter(pk=1).exists())

    def test_delete_user_failure_not_logged_in(self):
        """Тест неуспешного удаления пользователя без авторизации"""
        response = self.client.post(reverse("user_delete", kwargs={"pk": 1}))
        self.assertEqual(
            response.status_code, 302
        )  # Перенаправление на страницу логина
        self.assertTrue(User.objects.filter(pk=1).exists())

    def test_delete_user_failure_different_user(self):
        """Тест неуспешного удаления другого пользователя"""
        # Создаём второго пользователя
        User.objects.create_user(username="otheruser", password="password123")
        self.client.force_login(
            User.objects.get(username="otheruser")
        )  # Логинимся как другой пользователь
        response = self.client.post(reverse("user_delete", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 302)  # Ожидаем перенаправление
        self.assertTrue(User.objects.filter(pk=1).exists())
        # Проверяем, что сообщение об ошибке отображается
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "У вас нет прав для изменения другого пользователя.",
        )


class UserDeleteRedirectTests(TestCase):
    fixtures = ["users.json"]  # Загружаем фикстуру с пользователями

    def test_delete_user_redirect(self):
        """Тест перенаправления после удаления пользователя"""
        # Логинимся как пользователь с pk=2
        user = User.objects.get(pk=2)
        self.client.force_login(user)

        # Удаляем пользователя
        response = self.client.post(reverse("user_delete", kwargs={"pk": 2}))

        # Проверяем, что пользователь был удалён
        self.assertFalse(User.objects.filter(pk=2).exists())

        # Проверяем перенаправление на список пользователей
        self.assertRedirects(response, reverse("user_list"))
