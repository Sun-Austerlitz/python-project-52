from django import forms
from .models import Status


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ["name"]
        labels = {"name": "Имя"}

    def clean_name(self):
        """Удаляет лишние пробелы из имени статуса"""
        name = self.cleaned_data["name"]
        return name.strip()
