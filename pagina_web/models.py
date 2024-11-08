from django.db import models

class alumno(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    
class examen(models.Model):
    descripcion = models.CharField(max_length=100)

class materia(models.Model):
    nombre = models.CharField(max_length=30)

class rama(models.Model):
    nombre = models.CharField(max_length=30)
    idMateria = models.ForeignKey(materia, on_delete=models.CASCADE)

class examen_tiene_materias(models.Model):
    idExamen = models.ForeignKey(examen, on_delete=models.CASCADE)
    idMateria = models.ForeignKey(materia, on_delete=models.CASCADE)

class examen_tiene_ramas(models.Model):
    idExamen = models.ForeignKey(examen, on_delete=models.CASCADE)
    idRama = models.ForeignKey(materia, on_delete=models.CASCADE)

class pregunta(models.Model):
    descripcion = models.CharField(max_length=200)
    idRama = models.ForeignKey(materia, on_delete=models.CASCADE)

class respuesta(models.Model):
    descripcion = models.CharField(max_length=200)
    idPregunta = models.ForeignKey(pregunta, on_delete=models.CASCADE)
    esCorrecta = models.BooleanField(default=False)
