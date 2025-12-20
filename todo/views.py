from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, Appointment
from .forms import TaskForm, AppointmentForm
from datetime import datetime
from django.db.models import Sum, F
from django.db.models.functions import Extract
import calendar
from calendar import monthcalendar

# Dashboard view - shows both tasks and appointments
def dashboard(request):
    tasks = Task.objects.filter(complete=False).order_by('due')
    appointments = Appointment.objects.filter(complete=False).order_by('date', 'time')
    context = {
        'tasks': tasks, 
        'appointments': appointments
    }
    return render(request, 'todo/dashboard.html', context)

# ========== TASK VIEWS ==========

# Create task
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('todo:task-list')
    else:
        form = TaskForm()
    return render(request, 'todo/task_create.html', {'form': form})

# List all tasks
def task_list(request):
    tasks = Task.objects.all().order_by('-created')
    incomplete_tasks = tasks.filter(complete=False)
    completed_tasks = tasks.filter(complete=True)
    context = {
        'incomplete_tasks': incomplete_tasks,
        'completed_tasks': completed_tasks
    }
    return render(request, 'todo/task_list.html', context)

# View task detail
def view_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'todo/task_detail.html', {'task': task})

# Update task
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('todo:task-list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'todo/task_update.html', {'form': form, 'task': task})

# Delete task
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()
        return redirect('todo:task-list')
    return render(request, 'todo/task_confirm_delete.html', {'task': task})

# Toggle task complete
def toggle_task_complete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.complete = not task.complete
    task.save()
    return redirect(request.META.get('HTTP_REFERER', 'todo:task-list'))

# ========== APPOINTMENT VIEWS ==========

# Create appointment
def create_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('todo:appointment-list')
    else:
        form = AppointmentForm()
    return render(request, 'todo/appointment_create.html', {'form': form})

# List all appointments
def appointment_list(request):
    appointments = Appointment.objects.all().order_by('date', 'time')
    incomplete_appointments = appointments.filter(complete=False)
    completed_appointments = appointments.filter(complete=True)
    context = {
        'incomplete_appointments': incomplete_appointments,
        'completed_appointments': completed_appointments
    }
    return render(request, 'todo/appointment_list.html', context)

# View appointment detail
def view_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'todo/appointment_detail.html', {'appointment': appointment})

# Update appointment
def update_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('todo:appointment-list')
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'todo/appointment_update.html', {'form': form, 'appointment': appointment})

# Delete appointment
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        appointment.delete()
        return redirect('todo:appointment-list')
    return render(request, 'todo/appointment_confirm_delete.html', {'appointment': appointment})

# Toggle appointment complete
def toggle_appointment_complete(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.complete = not appointment.complete
    appointment.save()
    return redirect(request.META.get('HTTP_REFERER', 'todo:appointment-list'))

# ========== CALENDAR VIEW ==========

def calendar_view(request):
    # Get current year and month, or from query params
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    
    # Get calendar for the month
    cal = monthcalendar(year, month)
    
    # Get all appointments for the month
    appointments = Appointment.objects.filter(
        date__year=year, 
        date__month=month
    ).order_by('date', 'time')
    
    # Create a dictionary of appointments by day
    appointments_by_day = {}
    for appointment in appointments:
        day = appointment.date.day
        if day not in appointments_by_day:
            appointments_by_day[day] = []
        appointments_by_day[day].append(appointment)
    
    # Calculate previous and next month
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    context = {
        'calendar': cal,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'appointments_by_day': appointments_by_day,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'today': datetime.now().date()
    }
    
    return render(request, 'todo/calendar.html', context)
