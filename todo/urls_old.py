from django.urls import path
from . import views

app_name = 'todo' 

urlpatterns = [
    path('create/', views.create_task, name='create-task'),
    path('', views.task_list, name='task-list'),
    path('<int:task_id>/', views.view_task, name='view-task'),
    path('<int:task_id>/update/', views.update_task, name='update-task'),
    path('<int:task_id>/delete/', views.delete_task, name='delete-task'),
    
]