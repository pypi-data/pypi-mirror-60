from django.db import models

# Create your models here.

class Codigo(models.Model):
    codigo = models.CharField(max_length=5)
    telefono = models.CharField(max_length=12)
    fecha = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        managed = True