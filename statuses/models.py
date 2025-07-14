from django.db import models


class Status(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Название")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.name
