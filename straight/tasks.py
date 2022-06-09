import requests
from celery import shared_task, states
from projects import views, models
from users import models as usermodels
import datetime
from datetime import timezone
from django.utils import timezone as django_timezone
import pytz
from django.db.models import Q
from django.core.mail import send_mail
from . import settings

@shared_task(bind=True)
def test_func(self):
    print('checking subtask')
    utc = pytz.utc
    subtasks = models.SubTask.objects.all()
    nothing_changed = True
    for subtask in subtasks:
        project = models.Project.objects.get(id=subtask.task.project_id)
        if django_timezone.now() > utc.localize(datetime.datetime.strptime(subtask.end_date.strftime('%Y-%m-%d'), '%Y-%m-%d')) and (subtask.status == 'ip' or subtask.status == 'ns'):
            nothing_changed = False
            add_days = (django_timezone.now() - utc.localize(datetime.datetime.strptime(subtask.end_date.strftime('%Y-%m-%d'), '%Y-%m-%d'))).days + 1
            subtask.end_date = subtask.end_date + datetime.timedelta(days=add_days)
            subtask.save()
            #Send notification and email to user
            members = usermodels.Member.objects.filter(team_id=project.team_id)
            for member in members:
                user = usermodels.User.objects.get(id=member.user_id)
                #Send notification
                notification = models.Notification(user=user,
                                                    message='Subtask "' + subtask.name + '" has been rescheduled to "' + subtask.end_date.strftime('%Y-%m-%d') + '" due to deadline.',
                                                    link='/projects/' + project.slug + '/detail', is_read=False, created_at=django_timezone.now(), updated_at=django_timezone.now())
                notification.save()
                #Send email
                email_subject = 'STRAIGHT: Overdue Subtask'
                email_body = 'Subtask ' + subtask.name + ' has been rescheduled to ' + subtask.end_date.strftime('%Y-%m-%d') + ' due to deadline.'
                email_to = user.email
                send_mail(subject=email_subject, message=email_body, from_email=settings.EMAIL_HOST_USER, recipient_list=[email_to], fail_silently=True)
                    
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
        return 'nothing changed'
    else:
        return 'something changed'
    
@shared_task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
    return 'Request: {0!r}'.format(self.request)
