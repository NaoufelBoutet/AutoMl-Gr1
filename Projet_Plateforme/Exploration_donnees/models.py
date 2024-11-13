from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import pandas as pd


class Utilisateurs(models.Model):
    class Languages(models.TextChoices):
        AFRIQUE_DU_SUD = 'ZA', 'Afrique du Sud'
        ARGENTINE = 'AR', 'Argentine'
        AUSTRALIE = 'AU', 'Australie'
        BELGIQUE = 'BE', 'Belgique'
        BOLIVIE = 'BO', 'Bolivie'
        BRESIL = 'BR', 'Brésil'
        CANADA = 'CA', 'Canada'
        CAMBODGE = 'KH', 'Cambodge'
        CHILI = 'CL', 'Chili'
        CHINE = 'CN', 'Chine'
        COLOMBIE = 'CO', 'Colombie'
        ECUADOR = 'EC', 'Équateur'
        ESPAGNE = 'ES', 'Espagne'
        FILIPINES = 'PH', 'Philippines'
        FRANCE = 'FR', 'France'
        GUATEMALA = 'GT', 'Guatemala'
        INDE = 'IN', 'Inde'
        INDONESIE = 'ID', 'Indonésie'
        IRLANDE = 'IE', 'Irlande'
        ITALIE = 'IT', 'Italie'
        JAMAICA = 'JM', 'Jamaïque'
        JAPON = 'JP', 'Japon'
        MAURICE = 'MU', 'Maurice'
        MEXIQUE = 'MX', 'Mexique'
        PARAGUAY = 'PY', 'Paraguay'
        PAKISTAN = 'PK', 'Pakistan'
        PEROU = 'PE', 'Pérou'
        RUSSIE = 'RU', 'Russie'
        SRI_LANKA = 'LK', 'Sri Lanka'
        SUISSE = 'CH', 'Suisse'
        TAIWAN = 'TW', 'Taïwan'
        TUNISIE = 'TN', 'Tunisie'
        URUGUAY = 'UY', 'Uruguay'
        VENEZUELA = 'VE', 'Venezuela'
        VIETNAM = 'VN', 'Vietnam'
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_creation = models.DateTimeField(auto_now_add=True, null=True)  # Allow null for existing rows
    date_modification = models.DateTimeField(auto_now=True)
    email = models.EmailField(null=True)
    telephone = models.CharField(max_length=10, null=True)
    code_postal = models.IntegerField(null=True, blank=True)
    pays = models.CharField(max_length=100, null=True)
    mot_de_passe = models.CharField(max_length=100, null=True)
    confirmation_mot_de_passe = models.CharField(max_length=100, null=True)
    entreprise = models.CharField(max_length=100, null=True, blank=True)
    date_de_naissance = models.DateField(validators=[MinValueValidator(1930),
                                                      MaxValueValidator(2020)], null=True)
    sexe = models.BooleanField(null=True, blank=True)
    profession = models.CharField(max_length=100, null=True, blank=True)
    experience = models.IntegerField(validators=[MinValueValidator(0),
                                                  MaxValueValidator(5)], null=True)
    languages = models.CharField(choices=Languages.choices, max_length=4, null=True)


class Projet(models.Model): # Définition d'un modèle appelé "Projet".
    nom_Projet = models.CharField(max_length=50) # Ce champ représente le nom du projet, avec une longueur maximale de 50 caractères.
    file = models.FileField(upload_to='datasets')   
    # Ce champ permet de télécharger et de stocker un fichier
    # Le fichier sera stocké dans un sous-dossier appelé "datasets" du répertoire de fichiers de ton projet.
    def __str__(self):
        return self.nom_Projet
    # Cette méthode permet de définir ce qui sera retourné lorsqu'on affiche une instance de ce modèle en tant que chaîne.

##
# Classe ProjetDatasetViewer pour gérer l'affichage des datasets
class ProjetDatasetViewer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self.error = None

    def load_data(self):
        """Charge le dataset en fonction de l'extension du fichier."""
        try:
            if self.file_path.endswith('.csv'):
                self.data = pd.read_csv(self.file_path, encoding="latin-1")
            elif self.file_path.endswith('.xls') or self.file_path.endswith('.xlsx'):
                self.data = pd.read_excel(self.file_path)
            elif self.file_path.endswith('.txt'):
                self.data = pd.read_table(self.file_path)
            else:
                self.error = 'Type de fichier non supporté.'
        except Exception as e:
            self.error = f'Erreur lors du chargement du fichier : {str(e)}'

    def get_data(self):
        """Retourne le dataset ou une erreur s'il y a un problème lors du chargement."""
        if self.error:
            return None, self.error
        return self.data, None
    
    

