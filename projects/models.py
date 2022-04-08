from django.db import models

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    start_date = models.DateField()
    end_date = models.DateField()
    size = models.CharField(max_length=100)
    user_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name


class Task(models.Model):
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=100)
    size = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.IntegerField()
    def __str__(self):
        return self.name
