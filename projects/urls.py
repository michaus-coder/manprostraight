from django.urls import path, include
from django.contrib import auth
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:project_name>/detail', views.detail, name='detail'),
    path('store/', views.store, name='add_project'),
    path('<str:project_name>/store', views.store_task, name='store_task'),
    path('<str:project_name>/store_subtask', views.store_subtask, name='store_subtask'),
    path('<str:project_name>/store_material', views.store_material, name="store_material")
]
