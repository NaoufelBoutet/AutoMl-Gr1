from django.db import models

# Create your models here.

class File(models.Model):
    user = models.Charfield()
    name = models.Charfield(max_length=100)
    metadata = models.CharField
    def __str__(self):
        return self.name