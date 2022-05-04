from django.urls import path, include
from django.contrib import auth
from . import views

app_name = ''

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    # path('password_change/', views.change_password, name='change_password'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('', include('django.contrib.auth.urls'), {'redirect_if_logged_in': '/home'}),
    path('kontak/', views.contact, name='contact'),
    # path('accounts/', include('accounts.urls', namespace='')),
    path('usermanagement/', views.usermanagement, name='usermanagement'),
    path('notif/', views.notif, name='notif'),
    path('teammanagement/', views.teammanagement, name='teammanagement'),
    path('profile/', views.profile, name='profile'),
    path('welcome/', views.welcome, name='welcome'),
]
