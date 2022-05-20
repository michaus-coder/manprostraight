from django.urls import path, include
from django.contrib import auth
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:project_name>/detail', views.detail, name='detail'),
    path('store/', views.store, name='add_project'),
]
