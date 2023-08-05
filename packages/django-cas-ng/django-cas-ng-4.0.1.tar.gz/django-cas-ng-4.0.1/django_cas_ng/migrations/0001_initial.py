# Generated by Django 1.9.1 on 2016-01-13 18:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProxyGrantingTicket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, max_length=255, null=True)),
                ('pgtiou', models.CharField(blank=True, max_length=255, null=True)),
                ('pgt', models.CharField(blank=True, max_length=255, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SessionTicket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=255)),
                ('ticket', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='proxygrantingticket',
            unique_together={('session_key', 'user')},
        ),
    ]
