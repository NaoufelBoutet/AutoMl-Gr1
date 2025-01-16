from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='uploads/')
    def __str__(self):
        return self.name