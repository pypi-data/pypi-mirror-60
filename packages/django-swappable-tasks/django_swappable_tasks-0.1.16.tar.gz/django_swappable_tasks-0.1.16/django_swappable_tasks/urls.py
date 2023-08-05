from django.urls import path

from django_swappable_tasks import views

app_name = "django_swappable_tasks"

urlpatterns = [
    path('tasks/', views.TasksHandlerView.as_view(), name='tasks')
]
