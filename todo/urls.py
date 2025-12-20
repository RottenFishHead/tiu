from django.urls import path
from . import views

app_name = 'todo' 

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Task URLs
    path('tasks/', views.task_list, name='task-list'),
    path('tasks/create/', views.create_task, name='create-task'),
    path('tasks/<int:task_id>/', views.view_task, name='view-task'),
    path('tasks/<int:task_id>/update/', views.update_task, name='update-task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete-task'),
    path('tasks/<int:task_id>/toggle/', views.toggle_task_complete, name='toggle-task'),
    
    # Appointment URLs
    path('appointments/', views.appointment_list, name='appointment-list'),
    path('appointments/create/', views.create_appointment, name='create-appointment'),
    path('appointments/<int:appointment_id>/', views.view_appointment, name='view-appointment'),
    path('appointments/<int:appointment_id>/update/', views.update_appointment, name='update-appointment'),
    path('appointments/<int:appointment_id>/delete/', views.delete_appointment, name='delete-appointment'),
    path('appointments/<int:appointment_id>/toggle/', views.toggle_appointment_complete, name='toggle-appointment'),
    
    # Calendar
    path('calendar/', views.calendar_view, name='calendar'),
]
