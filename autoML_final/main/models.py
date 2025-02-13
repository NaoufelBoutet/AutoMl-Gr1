from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Project(models.Model):
    """Table qui stocke les projets liés à un utilisateur"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="projets"
    )
    projet_name = models.CharField(max_length=255, unique=True)  # Champ de nom du projet
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        # L'unicité sur 'user' et 'projet_name' reste présente
        unique_together = ('user', 'projet_name')  

    def __str__(self):
        return self.projet_name


class Dataset(models.Model):
    """Table qui stocke les datasets liés à un projet"""
    projet = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name="datasets"
    )
    dataset_name = models.CharField(max_length=255, unique=True)  # Champ de nom du dataset
    description = models.TextField(blank=True, null=True)

    class Meta:
        # L'unicité sur 'projet' et 'dataset_name' reste présente
        unique_together = ('projet', 'dataset_name')

    def __str__(self):
        return self.dataset_name


class Graphique(models.Model):
    """Table des graphiques liés à un dataset"""
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE, 
        related_name="graphiques"
    )
    graphique = models.CharField(max_length=100, unique=True)  # Champ de nom du graphique
    donnees = models.JSONField()

    def __str__(self):
        return self.graphique
