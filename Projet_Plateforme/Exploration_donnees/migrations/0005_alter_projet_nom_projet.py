# Generated by Django 5.1.1 on 2024-10-19 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Exploration_donnees', '0004_alter_projet_csv_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projet',
            name='nom_Projet',
            field=models.CharField(max_length=50),
        ),
    ]
