from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
import json
from django.contrib.auth import get_user_model

User = get_user_model()

from django.conf import settings
from django.db import models

class User_project(models.Model):
    """Table qui stocke les projets liés à un utilisateur"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        primary_key=True
    )
    projects = models.JSONField(default=dict)

    def add_project(self, project_name):
        """Créer un nouveau projet et l'associer à l'utilisateur"""
        project = ProjectsDatasets.objects.create(user_project=self)
        self.projects[str(project.id)] = project_name
        self.save()
        return project

class ProjectsDatasets(models.Model):
    """Table qui stocke les datasets liés à un projet"""
    user_project = models.OneToOneField(User_project, on_delete=models.CASCADE,primary_key=True)
    datasets = models.JSONField(default=dict)
    def add_dataset(self, dataset_name, dataset_id):
        """Ajoute un dataset au dictionnaire"""
        self.datasets[str(dataset_name)] = dataset_id
        self.save()