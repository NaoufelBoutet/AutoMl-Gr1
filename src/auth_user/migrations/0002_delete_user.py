# Generated by Django 5.1.1 on 2025-01-24 13:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth_user', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]
