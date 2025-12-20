from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm
from datetime import datetime
from django.db.models import Sum, F
from django.db.models.functions import Extract

# Create view
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('todo:task-list')
    else:
        form = TaskForm()
    return render(request, 'todo/create.html', {'form': form})

# Read/view all tasks
def task_list(request):
    tasks = Task.objects.filter(category=1, complete=False)
    appointments = Task.objects.filter(category=2, complete=False).order_by('due')
    context = {
        'tasks': tasks, 
        'appointments':appointments
    }
    return render(request, 'todo/list.html', context)

# Read/view a specific task
def view_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'todo/detail.html', {'task': task})

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
    return render(request, 'todo/update.html', {'form': form})

# Delete task
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()
        return redirect('task-list')
    return render(request, 'todo/delete.html', {'task': task})
