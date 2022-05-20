from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = ''

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    # path('password_change/', views.change_password, name='change_password'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('', include('django.contrib.auth.urls')),
    path('kontak/', views.contact, name='contact'),
    # path('accounts/', include('accounts.urls', namespace='')),
    path('usermanagement/', views.usermanagement, name='usermanagement'),
    path('notif/', views.notif, name='notif'),
    path('teammanagement/', views.teammanagement, name='teammanagement'),
    path('profile/', views.profile, name='profile'),
    path('welcome/', views.welcome, name='welcome'),
    path('usermanagement/create/', views.create_user, name='create_user'),
    path('usermanagement/update/<int:pk>', views.update_user, name='update_user'),
    path('usermanagement/delete/', views.delete_user, name='delete_user'),
    path('usermanagement/reset_password/', views.reset_password, name='reset_password'),
    path('<int:pk>/', views.detail, name='detail'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('create_team/', views.create_team, name='create_team'),
    path('delete_team/<int:id>', views.delete_team, name='delete_team'),
    path('teammanagement/team_user_list/<int:tid>', views.team_user_list, name='team_user_list'),
    path('teammanagement/add_team_member/', views.add_team_member, name='add_team_member'),
    path('teammanagement/remove_team_member/<int:pk>', views.remove_team_member, name='remove_team_member'),
]
