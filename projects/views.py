import datetime
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
    return render(request, '../templates/projects/detail.html', {'project': project})

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
