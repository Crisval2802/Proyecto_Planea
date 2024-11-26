from django.db import models
from  django.contrib.auth.models import User

class alumno(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    idUsuario = models.ForeignKey(User,  on_delete=models.DO_NOTHING, default=1)
    
class materia(models.Model):
    nombre = models.CharField(max_length=30)

class examen(models.Model):
    nombre = models.CharField(max_length=100)
    idMateria = models.ForeignKey(materia, on_delete=models.CASCADE, default=1)

class rama(models.Model):
    nombre = models.CharField(max_length=30)
    idMateria = models.ForeignKey(materia, on_delete=models.CASCADE)

class pregunta(models.Model):
    descripcion = models.CharField(max_length=500)
    idExamen = models.ForeignKey(examen, on_delete=models.CASCADE, default=1)
    idRama = models.ForeignKey(rama, on_delete=models.CASCADE)

class respuesta(models.Model):
    descripcion = models.CharField(max_length=500)
    idPregunta = models.ForeignKey(pregunta, on_delete=models.CASCADE)
    esCorrecta = models.BooleanField(default=False)

class intento(models.Model):
    idExamen = models.ForeignKey(examen, on_delete=models.DO_NOTHING)
    idAlumno = models.ForeignKey(alumno, on_delete=models.DO_NOTHING)
    estatus = models.CharField(max_length=20, default="PENDIENTE") # PENDIENTE - FINALIZADO
    resultado = models.FloatField(default=0)

class avances(models.Model):
    idIntento = models.ForeignKey(intento, on_delete=models.DO_NOTHING)
    idPregunta = models.ForeignKey(pregunta, on_delete=models.DO_NOTHING)
    idRespuesta = models.ForeignKey(respuesta, on_delete=models.CASCADE)