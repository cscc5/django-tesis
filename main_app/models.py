from django.db import models
# Create your models here.

class Trabajos(models.Model):

    titulo = models.CharField(max_length=200)
    ubicacion = models.CharField(max_length=50)
    compañia = models.CharField(max_length=50)
    latitud = models.FloatField()
    longitud = models.FloatField()
    class Meta:
        verbose_name = "Trabajo"
        verbose_name_plural = "Trabajos"
    def __str__(self):
        return self.titulo


class Trabajos_Clasificados(models.Model):

    titulo = models.CharField(max_length=200)
    clasificacion = models.IntegerField()
    class Meta:
        verbose_name = "Trabajo"
        verbose_name_plural = "Trabajos_Clasificados"
    def __str__(self):
        return self.titulo
    