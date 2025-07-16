import django_filters
from .models import Task


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter(
        queryset=Task.objects.values_list("status", flat=True)
    )
    executor = django_filters.ModelChoiceFilter(
        queryset=Task.objects.values_list("executor", flat=True)
    )
    labels = django_filters.ModelChoiceFilter(
        queryset=Task.objects.values_list("labels", flat=True)
    )

    class Meta:
        model = Task
        fields = ["status", "executor", "labels", "author"]
