from django.contrib import admin
from django.urls import path, include

from task_manager.users.views import CustomLoginView, CustomLogoutView
from .views import home, index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("users/", include("task_manager.users.urls")),
    path("statuses/", include("task_manager.statuses.urls")),
    path("tasks/", include("task_manager.tasks.urls")),
    path("labels/", include("task_manager.labels.urls")),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("rollbar-test/", index, name="rollbar_test"),
]
