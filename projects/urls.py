from django.urls import path, include
from django.contrib import auth
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:project_name>/detail', views.detail, name='detail'),
    path('store/', views.store, name='add_project'),
    path('<str:project_name>/store', views.store_task, name='store_task'),
    path('<str:project_name>/update', views.update_task, name="update_task"),
    path('<str:project_name>/delete', views.destroy_task, name="delete_task"),
    path('<str:project_name>/store_subtask', views.store_subtask, name='store_subtask'),
    path('<str:project_name>/update_subtask', views.update_subtask, name="update_subtask"),
    path('<str:project_name>/delete_subtask', views.destroy_subtask, name="delete_subtask"),
    path('<str:project_name>/store_material', views.store_material, name="store_material"),
    path('<str:project_name>/update_material', views.update_material, name="update_material"),
    path('<str:project_name>/delete_material', views.destroy_material, name="delete_material"),
]
