from django.urls import path, include
from . import views

app_name = ''

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    # path('password_change/', views.change_password, name='change_password'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('', include('django.contrib.auth.urls')),
]
