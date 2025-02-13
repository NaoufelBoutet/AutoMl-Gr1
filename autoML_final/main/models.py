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
    projet = models.CharField(max_length=255,primary_key=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def del_projet(self):
        """Supprimer un projet"""
        self.delete()

    class Meta:
        unique_together = ('user', 'projet')  # Un utilisateur ne peut pas avoir deux projets du même nom

class Dataset(models.Model):
    """Table qui stocke les datasets liés à un projet"""
    projet = models.ForeignKey(
        Project,  # On utilise le modèle Project ici
        on_delete=models.CASCADE, 
        related_name="datasets"
    )
    dataset = models.CharField(max_length=255,primary_key=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('projet', 'dataset')  # Un projet ne peut pas avoir deux datasets du même nom

class Graphique(models.Model):
    """Table des graphiques liés à un dataset"""
    dataset = models.ForeignKey(
        Dataset,  # On utilise le modèle Dataset ici
        on_delete=models.CASCADE, 
        related_name="graphiques"
    )
    graphique = models.CharField(max_length=100,primary_key=True)
    donnees = models.JSONField()
