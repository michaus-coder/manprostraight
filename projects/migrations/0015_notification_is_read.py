# Generated by Django 4.0.3 on 2022-06-09 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0014_notification_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
    ]
