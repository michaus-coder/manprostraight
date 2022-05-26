import datetime
from math import floor
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetDoneView
from django.utils.text import slugify
from . import models
from users import models as usermodels
from django.shortcuts import render
import pandas as pd
from plotly.offline import plot
import plotly.express as px

def home(request):
    return render(request, '../templates/home.html')

def index(request):
    allteam = usermodels.Team.objects.all()
    members = usermodels.Member.objects.filter(user_id=request.user.id)
    teams = usermodels.Team.objects.filter(id__in=members.values('team_id'))
    projects = models.Project.objects.filter(user_id__in=teams.values('user_id'))
    my_team = usermodels.Team.objects.filter(user_id=request.user.id)
    if request.user.is_superuser == 1:
        projects = models.Project.objects.all()
        
    return render(request, '../templates/projects/index.html', {'projects': projects, 'members': members, 'teams': allteam, 'my_team': my_team})

def detail(request, project_name):
    project = models.Project.objects.get(slug=project_name)
    tasks = models.Task.objects.filter(project_id=project.id)
    for task in tasks:
        if task.subtask_set.count() > 0:
            in_progress_subtasks = models.SubTask.objects.filter(task_id=task.id, status='ip')
            complete__subtasks = models.SubTask.objects.filter(task_id=task.id, status='c')
            task.overall_status = floor(((in_progress_subtasks.count()*50) + (complete__subtasks.count()*100)/task.subtask_set.count()))
        else:
            task.overall_status = 0

    latest_task = models.Task.objects.order_by('-updated_at').first()
    latest_subtask = models.SubTask.objects.filter(task_id__in=tasks.values('id')).order_by('-updated_at').first()
    latest_material = models.RawMaterial.objects.filter(project_id=project.id).order_by('-updated_at').first()
    subtasks = models.SubTask.objects.all()
    last_updated = max(latest_task.updated_at, latest_subtask.updated_at, latest_material.updated_at)
    subtasks_data = [
        {
        'Subtask': x.name,
        'Start Date': x.start_date,
        'End Date': x.end_date,
        'Status': x.status,
        } for x in subtasks
    ]
    df = pd.DataFrame(subtasks_data)
    fig = px.timeline(df, x_start='Start Date', x_end='End Date', y='Subtask', color='Status', width=1200)
    fig.update_yaxes(autorange="reversed")
    gantt_plot = plot(fig, output_type='div')

    return render(request, '../templates/projects/detail.html', {'project': project, 'tasks': tasks, 'last_updated': last_updated, 'gantt_plot': gantt_plot})

def store(request):
    project = models.Project()
    project.name = request.POST['name']
    project.description = request.POST['description']
    project.start_date = request.POST['start-date']
    project.end_date = request.POST['end-date']
    project.size = request.POST['size']
    project.user_id = request.user.id
    project.slug = slugify(project.name)
    project.created_at = datetime.datetime.now()
    project.updated_at = datetime.datetime.now()
    project.save()
    return redirect('projects:index')

def store_task(request, project_name):
    project = models.Project.objects.get(slug=project_name)
    task = models.Task()
    task.name = request.POST['name']
    task.start_date = request.POST['start-date']
    task.end_date = request.POST['end-date']
    task.project_id = project.id
    task.created_at = datetime.datetime.now()
    task.updated_at = datetime.datetime.now()
    task.save()
    return redirect('projects:detail', project_name=project_name)

def store_subtask(request, project_name):
    project = models.Project.objects.get(slug=project_name)
    task = models.Task.objects.get(id=request.POST['task_id'])
    subtask = models.SubTask()
    subtask.name = request.POST['name']
    subtask.start_date = request.POST['start-date']
    subtask.end_date = request.POST['end-date']
    subtask.status = request.POST['status']
    subtask.priority = request.POST['priority']
    subtask.task = task
    subtask.created_at = datetime.datetime.now()
    subtask.updated_at = datetime.datetime.now()
    subtask.save()
    return redirect('projects:detail', project_name=project_name)

def store_material(request, project_name):
    project = models.Project.objects.get(slug=project_name)
    material = models.RawMaterial()
    material.name = request.POST['name']
    material.quantity = request.POST['quantity']
    material.unit = request.POST['unit']
    material.status = request.POST['status']
    material.deadline = request.POST['deadline']
    material.project = project
    material.created_at = datetime.datetime.now()
    material.updated_at = datetime.datetime.now()
    material.save()
    return redirect('projects:detail', project_name=project_name)

