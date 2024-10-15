from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

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


class Projet(models.Model):
    nom_Projet = models.CharField(max_length=100)
    csv_file = models.FileField(upload_to='datasets')   
    def __str__(self):
        return self.nom_Projet
 

