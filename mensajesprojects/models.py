from django.db import models

# Create your models here.
#creacion del modelo para mensajes
class Mensaje_principalivr(models.Model):
    mensaje_principal = models.TextField(max_length=300)
    id_principal = models.IntegerField()
    fecha_ingreso = models.DateTimeField(auto_now_add=True)

