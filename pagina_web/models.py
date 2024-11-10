from django.db import models

class alumno(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    
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
