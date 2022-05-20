import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth import login, update_session_auth_hash 
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User
from .tokens import account_activation_token
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import render
from django.contrib import messages
from django.core.mail import send_mail
from . import forms
import json
from . import models

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your Straight Account'
            message = render_to_string('users/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('users:account_activation_sent')
    else:
        form = UserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('users:home')
    else:
        return render(request, 'users/account_activation_invalid.html')

def page_not_found(request, exception):
    return redirect('/login')

def login(request):
    user = request.user
    if user.is_authenticated:
        return redirect('users:home')
    else:
        return render(request, 'users/login.html')

def welcome(request):
    return render(request, 'welcome.html')

def usermanagement(request):
    users = User.objects.all()
    form = forms.UserForm()
    usercreationform = forms.UserCreationForm()
    userpasswordform = forms.UserPasswordForm()
    return render(request, 'usermanagement.html', {'users': users, 'form': form, 'usercreationform': usercreationform, 'userpasswordform': userpasswordform})

def notif(request):
	return render(request, 'notif.html')
	
def teammanagement(request):
    users = User.objects.all()
    teams = models.Team.objects.all()
    registered_member = models.Member.objects.filter(user_id=request.user.id).select_related('team')
    members = models.Member.objects.filter(team_id__in=registered_member.values('team_id'))
    team_count = models.Team.objects.filter(user_id=request.user.id).count()
    return render(request, 'teammanagement.html', {'users': users, 'teams': teams, 'members': members, 'team_count': team_count})

def profile(request):
    user = request.user
    return render(request, 'profile.html', {'user': request.user})

def team_user_list(request, tid):
    try:
        members = models.Member.objects.filter(team_id=tid)
    except models.Member.DoesNotExist:
        members = None

    if members:
        users = models.User.objects.exclude(id__in=members.values('user_id')).exclude(pk=request.user.id).exclude(is_superuser=True)
    else:
        users = models.User.objects.exclude(pk=request.user.id).exclude(is_superuser=True)

    return JsonResponse(serializers.serialize('json', users), safe=False)

def add_team_member(request):
    if request.method == 'POST':
        member = models.Member()
        member.team = models.Team.objects.get(pk=request.POST['team_id'])
        member.user = models.User.objects.get(pk=request.POST['user_id'])
        member.save()
        return redirect('teammanagement')
    else:
        return redirect('teammanagement')

def remove_team_member(request, pk):
    member = models.Member.objects.get(pk=pk)
    member.delete()
    return redirect('teammanagement')

@login_required
def contact(request):
	form = forms.ContactForm()
	if request.method == "POST":
		form = forms.ContactForm(request.POST)
		if form.is_valid():
			#Mengirim email
			send_mail(
				'Dari Kontak Rekan',
				request.POST['subject'],
				request.user.email,
				[request.POST['email']],
				fail_silently=False
			)
			messages.success(request, 'Email sent successfully!')
			return HttpResponseRedirect(reverse('contact'))

	return render(request, 'contact.html', {'form': form})

def create_user(request):
    usercreationform = forms.UserCreationForm()
    userpasswordform = forms.UserPasswordForm()
    if request.method == 'POST':
        form = forms.UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usermanagement')
        else:
            return redirect('usermanagement.html')
    else:
        form = UserCreationForm()
    return render(request, 'usermanagement.html', {'form': form, 'usercreationform': usercreationform, 'userpasswordform': userpasswordform})

def update_user(request, pk):
    usercreationform = forms.UserCreationForm()
    userpasswordform = forms.UserPasswordForm()
    if request.method == 'POST':
        user = User.objects.get(pk=pk)
        form = forms.UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('usermanagement')
    else:
        form = forms.UserForm(instance=request.user)
    return render(request, 'usermanagement.html', {'form': form, 'usercreationform': usercreationform, 'userpasswordform': userpasswordform})

def delete_user(request):
    user = User.objects.get(pk=request.POST['id'])
    user.delete()
    return redirect('usermanagement')

def detail(request, pk):
    user = User.objects.get(pk=pk)
    # serialized = serializers.serialize('json', [user,])
    # struct = json.loads(serialized)
    
    data = json.dumps({'first_name': getattr(user, 'first_name'), 'last_name': getattr(user, 'last_name'), 'email': getattr(user, 'email'), 'username': getattr(user, 'username')})
    return HttpResponse(data, content_type='application/json')

def reset_password(request):
    if request.method == 'POST':
        user = User.objects.get(pk=request.POST['id'])
        form = forms.UserPasswordForm(request.POST, instance=user)
        if form.is_valid():
            user.set_password(request.POST['password'])
            user.save()
            messages.success(request, 'Password was successfully updated!')
            return redirect('usermanagement')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = forms.UserPasswordForm(request.user)
    return redirect('usermanagement')

def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.email = request.POST['email']
        if request.POST['password']:
            user.set_password(request.POST['password'])
        user.save()
        update_session_auth_hash(request, user)
    else:
        form = forms.UserForm(instance=request.user)
    return redirect('profile')

def create_team(request):
    if request.method == 'POST':
        user = User.objects.get(pk=request.POST['user_id'])
        team = models.Team(name=request.POST['name'], user=user, created_at = datetime.datetime.now(), updated_at = datetime.datetime.now())
        team.save()
        member = models.Member(team=team, user=user, created_at = datetime.datetime.now(), updated_at = datetime.datetime.now())
        member.save()
    return redirect('teammanagement')

def delete_team(request, id):
    team = models.Team.objects.get(pk=id)
    team.delete()
    return redirect('teammanagement')

