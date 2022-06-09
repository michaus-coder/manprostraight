import datetime
from datetime import timezone
import time
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
from django.db.models import Q
from straight.tasks import test_func

def check_subtask_periodic():
    subtasks = models.SubTask.objects.all()
    nothing_changed = True
    for subtask in subtasks:
        project = models.Project.objects.get(id=subtask.task.project_id)
        if datetime.datetime.now() > subtask.end_date:
            nothing_changed = False
            add_days = 1
            subtask.end_date = subtask.end_date + datetime.timedelta(days=1)
            subtask.save()
            after_subtask = models.SubTask.objects.filter(task=subtask.task).filter(start_date__gt=subtask.start_date).filter(~Q(id=subtask.id))
            for x in after_subtask:
                if x.status == 'ns':
                    x.start_date = x.start_date + datetime.timedelta(days=add_days)
                x.end_date = x.end_date + datetime.timedelta(days=add_days)
                x.save()
            raw_materials = models.RawMaterial.objects.filter(project_id=project.id).filter(status=0).filter(deadline__gte=subtask.start_date)
            for x in raw_materials:
                x.deadline = x.deadline + datetime.timedelta(days=add_days)
                x.save()
            subtask.task.end_date = subtask.task.end_date + datetime.timedelta(days=add_days)
            if subtask.task.end_date > project.end_date:
                project.end_date = subtask.task.end_date
                project.save()
            subtask.task.save()
            tasks = models.Task.objects.filter(project_id=project.id).filter(start_date__gte=subtask.task.start_date).filter(~Q(id=subtask.task.id))
            for x in tasks:
                x.start_date = x.start_date + datetime.timedelta(days=add_days)
                x.end_date = x.end_date + datetime.timedelta(days=add_days)
                for subtask in x.subtask_set.all():
                    if subtask.status == 'ns':
                        subtask.start_date = subtask.start_date + datetime.timedelta(days=add_days)
                    subtask.end_date = subtask.end_date + datetime.timedelta(days=add_days)
                    subtask.save()
                if x.end_date > project.end_date:
                    project.end_date = x.end_date
                    project.save()
                x.save()
    if nothing_changed:
        return HttpResponse('nothing changed', status=201)
    else:
        return HttpResponse('something changed', status=200)
        

def home(request):
    members = usermodels.Member.objects.filter(user_id=request.user.id)
    teams = []
    for member in members:
        teams.append(member.team)

    notifications_count = models.Notification.objects.filter(user_id=request.user.id).filter(is_read=False).count()
    projects_count = models.Project.objects.filter(team_id__in=teams).filter(end_date__gte=datetime.datetime.now()).count()
    return render(request, '../templates/home.html', {'notifications_count': notifications_count, 'projects_count': projects_count, 'teams': teams})

def index(request):
    allteam = usermodels.Team.objects.all()
    members = usermodels.Member.objects.filter(user_id=request.user.id)
    teams = usermodels.Team.objects.filter(id__in=members.values('team_id'))
    projects = models.Project.objects.filter(user_id__in=teams.values('user_id'))
    for project in projects:
        tasks = models.Task.objects.filter(project_id=project.id).order_by('start_date')
        latest_task = models.Task.objects.filter(project_id=project.id).order_by('-updated_at').first()
        latest_subtask = models.SubTask.objects.filter(task_id__in=tasks.values('id')).order_by('-updated_at').first()
        latest_material = models.RawMaterial.objects.filter(project_id=project.id).order_by('-updated_at').first()
        task_updated_at = datetime.datetime.strptime('2021-07-15T00:22:02+0000', '%Y-%m-%dT%H:%M:%S%z')
        subtask_updated_at = datetime.datetime.strptime('2021-07-15T00:22:02+0000', '%Y-%m-%dT%H:%M:%S%z')
        material_updated_at = datetime.datetime.strptime('2021-07-15T00:22:02+0000', '%Y-%m-%dT%H:%M:%S%z')
        if latest_task:
            task_updated_at = latest_task.updated_at
        if latest_subtask:
            subtask_updated_at = latest_subtask.updated_at
        if latest_material:
            material_updated_at = latest_material.updated_at
        subtasks = models.SubTask.objects.all().order_by('start_date')
        raw_materials = models.RawMaterial.objects.filter(project_id=project.id).order_by('deadline')
        last_updated = max(task_updated_at, subtask_updated_at, material_updated_at, project.updated_at)
        difference_day = abs((last_updated - datetime.datetime.now(timezone.utc)).days) - 1
        project.last_updated = difference_day

    my_team = usermodels.Team.objects.filter(user_id=request.user.id)
    if request.user.is_superuser == 1:
        projects = models.Project.objects.all()
        for project in projects:
            tasks = models.Task.objects.filter(project_id=project.id).order_by('start_date')
            latest_task = models.Task.objects.filter(project_id=project.id).order_by('-updated_at').first()
            latest_subtask = models.SubTask.objects.filter(task_id__in=tasks.values('id')).order_by('-updated_at').first()
            latest_material = models.RawMaterial.objects.filter(project_id=project.id).order_by('-updated_at').first()
            task_updated_at = datetime.datetime.strptime('2021-07-15T00:22:02+0000', '%Y-%m-%dT%H:%M:%S%z')
            subtask_updated_at = datetime.datetime.strptime('2021-07-15T00:22:02+0000', '%Y-%m-%dT%H:%M:%S%z')
            material_updated_at = datetime.datetime.strptime('2021-07-15T00:22:02+0000', '%Y-%m-%dT%H:%M:%S%z')
            if latest_task:
                task_updated_at = latest_task.updated_at
            if latest_subtask:
                subtask_updated_at = latest_subtask.updated_at
            if latest_material:
                material_updated_at = latest_material.updated_at
            subtasks = models.SubTask.objects.all().order_by('start_date')
            raw_materials = models.RawMaterial.objects.filter(project_id=project.id).order_by('deadline')
            last_updated = max(task_updated_at, subtask_updated_at, material_updated_at, project.updated_at)
            difference_day = abs((last_updated - datetime.datetime.now(timezone.utc)).days) - 1
            project.last_updated = difference_day
        
    return render(request, '../templates/projects/index.html', {'projects': projects, 'members': members, 'teams': allteam, 'my_team': my_team})

def detail(request, project_name):
    project = models.Project.objects.get(slug=project_name)
    tasks = models.Task.objects.filter(project_id=project.id).order_by('start_date')
    members = usermodels.Member.objects.filter(team_id=project.team_id)
    for task in tasks:
        if task.subtask_set.count() > 0:
            in_progress_subtasks = models.SubTask.objects.filter(task_id=task.id, status='ip')
            complete__subtasks = models.SubTask.objects.filter(task_id=task.id, status='c')
            task.overall_status = floor((((in_progress_subtasks.count()*50) + (complete__subtasks.count()*100))/task.subtask_set.count()))
        else:
            task.overall_status = 0

    latest_task = models.Task.objects.filter(project_id=project.id).order_by('-updated_at').first()
    latest_subtask = models.SubTask.objects.filter(task_id__in=tasks.values('id')).order_by('-updated_at').first()
    latest_material = models.RawMaterial.objects.filter(project_id=project.id).order_by('-updated_at').first()
    task_updated_at = datetime.datetime.strptime('2021-07-15T00:22:02+0000', '%Y-%m-%dT%H:%M:%S%z')
    subtask_updated_at = datetime.datetime.strptime('2021-07-15T00:22:02+0000', '%Y-%m-%dT%H:%M:%S%z')
    material_updated_at = datetime.datetime.strptime('2021-07-15T00:22:02+0000', '%Y-%m-%dT%H:%M:%S%z')
    if latest_task:
        task_updated_at = latest_task.updated_at
    if latest_subtask:
        subtask_updated_at = latest_subtask.updated_at
    if latest_material:
        material_updated_at = latest_material.updated_at
    
    subtasks = models.SubTask.objects.filter(task__in=tasks).order_by('start_date')
    raw_materials = models.RawMaterial.objects.filter(project_id=project.id).order_by('deadline')
    last_updated = max(task_updated_at, subtask_updated_at, material_updated_at, project.updated_at)
    gantt_plot = "Data not Available"
    if subtasks:
        subtasks_data = [
            {
            'Subtask': x.name,
            'Start Date': datetime.datetime.strptime(x.start_date.strftime('%Y-%m-%d') + 'T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
            'End Date': datetime.datetime.strptime(x.end_date.strftime('%Y-%m-%d') + 'T23:59:59+0000', '%Y-%m-%dT%H:%M:%S%z'),
            'Status': 'Not Started' if x.status == 'ns' else 'In Progress' if x.status == 'ip' else 'Completed',
            } for x in subtasks
        ]
        for x in raw_materials:
            subtasks_data.append({
            'Subtask': x.name + ' ' + str(x.quantity) + ' ' + x.unit,
            'Start Date': datetime.datetime.strptime(x.deadline.strftime('%Y-%m-%d') + 'T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
            'End Date': datetime.datetime.strptime(x.deadline.strftime('%Y-%m-%d') + 'T23:59:59+0000', '%Y-%m-%dT%H:%M:%S%z'),
            'Status': 'Arrived' if x.status == 0 else 'Pending',
            })

        subtasks_data.sort(key = lambda x: datetime.datetime.strptime(x['Start Date'].strftime('%Y-%m-%d'), '%Y-%m-%d'))
        df = pd.DataFrame(subtasks_data)
        fig = px.timeline(df, x_start='Start Date', x_end='End Date', y='Subtask', width=1200)
        fig.update_yaxes(autorange="reversed")
        gantt_plot = plot(fig, output_type='div')

    return render(request, '../templates/projects/detail.html', {'project': project, 'tasks': tasks, 'members' : members, 'last_updated': last_updated, 'gantt_plot': gantt_plot})

def store(request):
    project = models.Project()
    project.name = request.POST['name']
    project.description = request.POST['description']
    project.start_date = request.POST['start-date']
    project.end_date = request.POST['end-date']
    project.size = request.POST['size']
    project.user_id = request.user.id
    project.slug = slugify(project.name)
    project.team_id = request.POST['team']
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
    task.user_id = request.POST['pic']
    task.save()
    return redirect('projects:detail', project_name=project_name)

def update_task(request, project_name):
    project = models.Project.objects.get(slug=project_name)
    task = models.Task.objects.get(id=request.POST['task_id'])
    for subtask in task.subtask_set.all():
        if subtask.start_date < task.start_date:
            subtask.start_date = task.start_date
            subtask.save()
        elif subtask.end_date > task.end_date:
            subtask.end_date = task.end_date
            subtask.save()

    task.name = request.POST['name']
    task.start_date = request.POST['start-date']
    task.end_date = request.POST['end-date']
    task.updated_at = datetime.datetime.now()
    task.user_id = request.POST['pic']
    task.save()
    return redirect('projects:detail', project_name=project_name)

def reschedule_task(request, project_name):
    project = models.Project.objects.get(slug=project_name)
    task = models.Task.objects.get(id=request.POST['task_id'])
    # Reschedulling Feature
    if datetime.datetime.strptime(request.POST['end-date'], '%Y-%m-%d') > datetime.datetime.strptime(task.end_date.strftime('%Y-%m-%d'), '%Y-%m-%d'): #push back deadline
        difference_day = (datetime.datetime.strptime(request.POST['end-date'], '%Y-%m-%d') - datetime.datetime.strptime(task.end_date.strftime('%Y-%m-%d'), '%Y-%m-%d')).days
        for subtask in task.subtask_set.all():
            # if datetime.datetime.strptime(subtask.start_date.strftime('%Y-%m-%d'), '%Y-%m-%d') < datetime.datetime.strptime(request.POST['start-date'], '%Y-%m-%d') :
            #     subtask.start_date = request.POST['start-date']
            if subtask.status == 'ns':
                subtask.start_date = subtask.start_date + datetime.timedelta(days=difference_day)
            subtask.end_date = subtask.end_date + datetime.timedelta(days=difference_day)
            subtask.save()
        tasks = models.Task.objects.filter(project_id=project.id).filter(start_date__gte=task.start_date).filter(~Q(id=task.id))
        for x in tasks:
            x.start_date = x.start_date + datetime.timedelta(days=difference_day)
            x.end_date = x.end_date + datetime.timedelta(days=difference_day)
            for subtask in x.subtask_set.all():
                subtask.start_date = subtask.start_date + datetime.timedelta(days=difference_day)
                subtask.end_date = subtask.end_date + datetime.timedelta(days=difference_day)
                subtask.save()
            if x.end_date > project.end_date:
                project.end_date = x.end_date
                project.save()
            x.save()
        raw_materials = models.RawMaterial.objects.filter(project_id=project.id).filter(status=0)
        for x in raw_materials:
            x.deadline = x.deadline + datetime.timedelta(days=difference_day)
            x.save()
    elif datetime.datetime.strptime(request.POST['end-date'], '%Y-%m-%d')  < datetime.datetime.strptime(task.end_date.strftime('%Y-%m-%d'), '%Y-%m-%d'): #push forward deadline
        difference_day = (datetime.datetime.strptime(task.end_date.strftime('%Y-%m-%d'), '%Y-%m-%d') - datetime.datetime.strptime(request.POST['end-date'], '%Y-%m-%d')).days
        for subtask in task.subtask_set.all():
            # if datetime.datetime.strptime(subtask.start_date.strftime('%Y-%m-%d'), '%Y-%m-%d') < datetime.datetime.strptime(request.POST['start-date'], '%Y-%m-%d') :
            #     subtask.start_date = request.POST['start-date']
            if subtask.status == 'ns':
                subtask.start_date = subtask.start_date - datetime.timedelta(days=difference_day)
                if subtask.start_date < task.start_date:
                    task.start_date = subtask.start_date
                    task.save()
            subtask.end_date = subtask.end_date - datetime.timedelta(days=difference_day)
            subtask.save()
        tasks = models.Task.objects.filter(project_id=project.id).filter(start_date__gte=task.start_date).filter(~Q(id=task.id))
        for x in tasks:
            x.start_date = x.start_date - datetime.timedelta(days=difference_day)
            x.end_date = x.end_date - datetime.timedelta(days=difference_day)
            for subtask in x.subtask_set.all():
                subtask.start_date = subtask.start_date - datetime.timedelta(days=difference_day)
                if subtask.start_date < task.start_date:
                    task.start_date = subtask.start_date
                    task.save()
                subtask.end_date = subtask.end_date - datetime.timedelta(days=difference_day)
                subtask.save()
            if x.start_date < project.start_date:
                project.start_date = x.start_date
                project.save()
            x.save()
        raw_materials = models.RawMaterial.objects.filter(project_id=project.id).filter(status=0)
        for x in raw_materials:
            x.deadline = x.deadline - datetime.timedelta(days=difference_day)
            x.save()

    task.end_date = request.POST['end-date']
    if datetime.datetime.strptime(task.end_date, '%Y-%m-%d') > datetime.datetime.strptime(project.end_date.strftime('%Y-%m-%d'), '%Y-%m-%d'):
        project.end_date = task.end_date
        project.save()
    task.save()
    return redirect('projects:detail', project_name=project_name)

def destroy_task(request, project_name):
    project = models.Project.objects.get(slug=project_name)
    task = models.Task.objects.get(id=request.POST['task_id'])
    task.delete()
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

def update_subtask(request, project_name):
    project = models.Project.objects.get(slug=project_name)
    subtask = models.SubTask.objects.get(id=request.POST['subtask_id'])

    subtask = models.SubTask.objects.get(id=request.POST['subtask_id'])
    subtask.name = request.POST['name']
    subtask.start_date = request.POST['start-date']
    subtask.end_date = request.POST['end-date']
    subtask.status = request.POST['status']
    subtask.priority = request.POST['priority']
    subtask.updated_at = datetime.datetime.now()
    subtask.save()
    return redirect('projects:detail', project_name=project_name)

def reschedule_subtask(request, project_name):
    project = models.Project.objects.get(slug=project_name)
    subtask = models.SubTask.objects.get(id=request.POST['subtask_id'])
    
    #Reschedule subtask
    if datetime.datetime.strptime(request.POST['end-date'], '%Y-%m-%d') > datetime.datetime.strptime(subtask.end_date.strftime('%Y-%m-%d'), '%Y-%m-%d'): #push back deadline
        difference_day = (datetime.datetime.strptime(request.POST['end-date'], '%Y-%m-%d') - datetime.datetime.strptime(subtask.end_date.strftime('%Y-%m-%d'), '%Y-%m-%d')).days
        subtasks = models.SubTask.objects.filter(task_id=subtask.task_id).filter(start_date__gte=subtask.start_date).filter(~Q(id=subtask.id))
        for x in subtasks:
            if x.status == 'ns':
                x.start_date = x.start_date + datetime.timedelta(days=difference_day)
            x.end_date = x.end_date + datetime.timedelta(days=difference_day)
            x.save()
        raw_materials = models.RawMaterial.objects.filter(project_id=project.id).filter(status=0)
        for x in raw_materials:
            x.deadline = x.deadline + datetime.timedelta(days=difference_day)
            x.save()
        subtask.task.end_date = subtask.task.end_date + datetime.timedelta(days=difference_day)
        if subtask.task.end_date > project.end_date:
            project.end_date = subtask.task.end_date
            project.save()
        subtask.task.save()
        tasks = models.Task.objects.filter(project_id=project.id).filter(start_date__gte=subtask.task.start_date).filter(~Q(id=subtask.task.id))
        for x in tasks:
            x.start_date = x.start_date + datetime.timedelta(days=difference_day)
            x.end_date = x.end_date + datetime.timedelta(days=difference_day)
            for subtask in x.subtask_set.all():
                if subtask.status == 'ns':
                    subtask.start_date = subtask.start_date + datetime.timedelta(days=difference_day)
                subtask.end_date = subtask.end_date + datetime.timedelta(days=difference_day)
                subtask.save()
            if x.end_date > project.end_date:
                project.end_date = x.end_date
                project.save()
            x.save()
    elif datetime.datetime.strptime(request.POST['end-date'], '%Y-%m-%d')  < datetime.datetime.strptime(subtask.end_date.strftime('%Y-%m-%d'), '%Y-%m-%d'): #push forward deadline
        difference_day = (datetime.datetime.strptime(subtask.end_date.strftime('%Y-%m-%d'), '%Y-%m-%d') - datetime.datetime.strptime(request.POST['end-date'], '%Y-%m-%d')).days
        subtasks = models.SubTask.objects.filter(task_id=subtask.task_id).filter(start_date__gte=subtask.start_date).filter(~Q(id=subtask.id))
        for x in subtasks:
            x.start_date = x.start_date - datetime.timedelta(days=difference_day)
            if x.start_date < x.task.start_date:
                x.task.start_date = x.start_date
                x.task.save()
            x.end_date = x.end_date - datetime.timedelta(days=difference_day)
            x.save()
        raw_materials = models.RawMaterial.objects.filter(project_id=project.id).filter(status=0)
        for x in raw_materials:
            x.deadline = x.deadline - datetime.timedelta(days=difference_day)
            x.save()
        subtask.task.end_date = subtask.task.end_date - datetime.timedelta(days=difference_day)
        if subtask.task.start_date < project.start_date:
            project.start_date = subtask.task.start_date
            project.save()
        subtask.task.save()
        tasks = models.Task.objects.filter(project_id=project.id).filter(start_date__gte=subtask.task.start_date).filter(~Q(id=subtask.task.id))
        for x in tasks:
            x.start_date = x.start_date - datetime.timedelta(days=difference_day)
            x.end_date = x.end_date - datetime.timedelta(days=difference_day)
            for subtask in x.subtask_set.all():
                subtask.start_date = subtask.start_date - datetime.timedelta(days=difference_day)
                if subtask.start_date < x.start_date:
                    subtask.task.start_date = subtask.start_date
                    subtask.task.save()
                subtask.end_date = subtask.end_date - datetime.timedelta(days=difference_day)
                subtask.save()
            if x.start_date < project.start_date:
                project.start_date = x.start_date
                project.save()
            x.save()

    subtask = models.SubTask.objects.get(id=request.POST['subtask_id'])
    subtask.end_date = request.POST['end-date']
    subtask.save()
    return redirect('projects:detail', project_name=project_name)

def destroy_subtask(request, project_name):
    project = models.Project.objects.get(slug=project_name)
    subtask = models.SubTask.objects.get(id=request.POST['subtask_id'])
    subtask.delete()
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

def update_material(request, project_name):
    project = models.Project.objects.get(slug=project_name)
    material = models.RawMaterial.objects.get(id=request.POST['material_id'])
    material.name = request.POST['name']
    material.quantity = request.POST['quantity']
    material.unit = request.POST['unit']
    material.status = request.POST['status']
    material.deadline = request.POST['deadline']
    material.updated_at = datetime.datetime.now()
    material.save()
    return redirect('projects:detail', project_name=project_name)

def destroy_material(request, project_name):
    project = models.Project.objects.get(slug=project_name)
    material = models.RawMaterial.objects.get(id=request.POST['material_id'])
    material.delete()
    return redirect('projects:detail', project_name=project_name)

def delete_notification(request, nid):
    notification = models.Notification.objects.get(id=nid)
    notification.delete()
    return redirect('notif')