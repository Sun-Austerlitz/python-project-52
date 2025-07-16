from django.db import models
from django.contrib.auth.models import User

from task_manager.labels.models import Label
from task_manager.statuses.models import Status


class Task(models.Model):
    name = models.CharField(max_length=150, verbose_name="Имя задачи")
    description = models.TextField(blank=True, verbose_name="Описание")
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        verbose_name="Статус",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="authored_tasks",
        verbose_name="Автор",
    )
    executor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="executed_tasks",
        verbose_name="Исполнитель",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    labels = models.ManyToManyField(
        Label,
        blank=True,
        related_name="tasks",
        verbose_name="Метки",
    )

    def __str__(self):
        return self.name
