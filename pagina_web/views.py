from django.forms import model_to_dict
from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Prefetch
from django.contrib.auth.models import User
from .models import avances, examen, intento, materia, pregunta, rama, respuesta, alumno
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.serializers import serialize

import json


from .decorators import token_required
from django.utils.decorators import method_decorator

#Clases y funciones para la aplicacion web
class Login(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self,request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            datos={'message': "Credenciales incorrectas"}
            return render(request, 'login.html' , {"datos":datos})

class Inicio(View):
    @method_decorator(staff_member_required(login_url='login'), name='dispatch')
    def get(self, request):
        ramas_prefetch = Prefetch('rama_set', queryset=rama.objects.all(), to_attr='ramas')
        materias = materia.objects.prefetch_related(ramas_prefetch).all()
        examenes = examen.objects.all().order_by("id")
        return render(request, 'inicio.html', {'materias': materias, "examenes":examenes})
    
class PadronAlumnos(View):
    @method_decorator(staff_member_required(login_url='login'), name='dispatch')
    def get(self, request):
        alumnos = alumno.objects.all().order_by("id")
        return render(request, 'padron_alumnos.html', {"alumnos":alumnos})

class Examen(View):
    @method_decorator(staff_member_required(login_url='login'), name='dispatch')
    def get(self, request, id=0):
        resultado = examen.objects.filter(id=id).count()
        if resultado:
            auxExamen = examen.objects.get(id=id)
            respuestas_prefetch = Prefetch('respuesta_set', queryset=respuesta.objects.all(), to_attr='respuestas')
            preguntas = pregunta.objects.filter(idExamen_id=auxExamen.id).prefetch_related(respuestas_prefetch).all() #.order_by("idRama")
            ramas = rama.objects.filter(idMateria_id=auxExamen.idMateria).values
            return render(request, 'examen.html', {"examen": auxExamen, "preguntas": preguntas, "ramas": ramas})
        return redirect('/')

class Logout(View):
    def post(self, request):
        logout(request)
        return redirect('login')
    
@method_decorator(staff_member_required(login_url='login'), name='dispatch') #decorador que exige que el usuario logeado sea staff
def agregar_materia(request):
    if request.method == "POST":
        data = json.loads(request.body)
        nombre = data.get("nombre")
        if nombre:
            nueva_materia = materia(nombre=nombre)
            nueva_materia.save()
            return JsonResponse({"success": True})
        
@method_decorator(staff_member_required(login_url='login'), name='dispatch')
def agregar_rama(request):
    if request.method == "POST":
        data = json.loads(request.body)
        nombre = data.get("nombre")
        idMateria = data.get("idMateria")
        if nombre:
            nueva_rama = rama(nombre=nombre, idMateria_id=idMateria)
            nueva_rama.save()
            return JsonResponse({"success": True})

@method_decorator(staff_member_required(login_url='login'), name='dispatch')        
def agregar_examen(request):
    if request.method == "POST":
        data = json.loads(request.body)
        nombre = data.get("nombre")
        idMateria = data.get("idMateria")
        if nombre:
            nuevo_examen = examen(nombre=nombre, idMateria_id=idMateria)
            nuevo_examen.save()
            return JsonResponse({"success": True})

@method_decorator(staff_member_required(login_url='login'), name='dispatch')        
def agregar_pregunta(request):
    if request.method == "POST":
        data = json.loads(request.body)
        idExamen = data.get("idExamen")
        descripcionPregunta = data.get("descripcionPregunta")
        idRama = data.get("idRama")
        nueva_pregunta = pregunta(descripcion=descripcionPregunta, idExamen_id=idExamen, idRama_id=idRama)
        nueva_pregunta.save()

        respuesta1 = data.get("respuesta1")
        respuesta2 = data.get("respuesta2")
        respuesta3 = data.get("respuesta3")
        respuesta4 = data.get("respuesta4")

        correcta = data.get("correcta")
        if (correcta=="respuesta1"):
            nueva_respuesta=respuesta(descripcion = respuesta1, idPregunta_id= nueva_pregunta.id, esCorrecta=1)
        else:
            nueva_respuesta=respuesta(descripcion = respuesta1, idPregunta_id= nueva_pregunta.id, esCorrecta=0)
        nueva_respuesta.save()

        if (correcta=="respuesta2"):
            nueva_respuesta=respuesta(descripcion = respuesta2, idPregunta_id= nueva_pregunta.id, esCorrecta=1)
        else:
            nueva_respuesta=respuesta(descripcion = respuesta2, idPregunta_id= nueva_pregunta.id, esCorrecta=0)
        nueva_respuesta.save()

        if (correcta=="respuesta3"):
            nueva_respuesta=respuesta(descripcion = respuesta3, idPregunta_id= nueva_pregunta.id, esCorrecta=1)
        else:
            nueva_respuesta=respuesta(descripcion = respuesta3, idPregunta_id= nueva_pregunta.id, esCorrecta=0)
        nueva_respuesta.save()

        if (correcta=="respuesta4"):
            nueva_respuesta=respuesta(descripcion = respuesta4, idPregunta_id= nueva_pregunta.id, esCorrecta=1)
        else:
            nueva_respuesta=respuesta(descripcion = respuesta4, idPregunta_id= nueva_pregunta.id, esCorrecta=0)
        nueva_respuesta.save()
        
        return JsonResponse({"success": True})

class RegistrarUsuario(View):
    def get(self, request):
        return render(request, 'registrar_usuario.html')

    def post (self,request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            datos={'message': "Error, ya existe un registro con ese username"}
            return render(request, 'registrar_usuario.html' , {"datos":datos})
        else:
            user = User.objects.create_user(username, email, password)
            user.is_superuser=True
            user.is_staff=True
            user.save()
            return redirect("login")


class RegistrarAlumno(View):
    #@method_decorator(token_required)
    def post (self,request):
        data = json.loads(request.body)
        nombre = data.get("nombre")
        apellido=data.get("apellido")
        username=data.get("username")
        password = data.get("password")
        if User.objects.filter(username=username).exists():
            return JsonResponse({"success": False})
        else:
            user = User.objects.create_user(username, username, password)
            user.is_superuser=False
            user.is_staff=False
            user.save()
            nuevoAlumno = alumno(nombre=nombre, apellido=apellido, idUsuario=user)
            nuevoAlumno.save()
            return JsonResponse({"success": True})
        
#APIS para la aplicacion de flutter
class API_Inicio(View):
    #@method_decorator(token_required)
    def get(self, request):
        examenes = examen.objects.all().values().order_by("id")
        examenes = list(examenes)
        return JsonResponse({'message': "Bienvenido", "examenes": examenes})

class API_Examen(View):
    #@method_decorator(token_required)
    def get(self, request, id=0):
        if (id):
            auxExamen = examen.objects.get(id=id)
            respuestas_prefetch = Prefetch('respuesta_set', queryset=respuesta.objects.all(), to_attr='respuestas')
            preguntas = pregunta.objects.filter(idExamen_id=auxExamen.id).prefetch_related(respuestas_prefetch) #.order_by("idRama")
            auxExamen = model_to_dict(auxExamen)
            #Las respuestas se deben empalmar aparte para poder devolverlas en un json
            preguntas=obtenerPreguntas(id)
            return JsonResponse({'message': "Exito", "examen": auxExamen, "preguntas": preguntas})
        else:
            return JsonResponse({'message': "Error, debe proporcionar un id"})

class API_Intento(View):

    def get(self, request, idUsuario=0, idExamen=0):
        if (id):
            auxAlumno = alumno.objects.get(idUsuario=idUsuario)
            auxExamen = examen.objects.get(id=idExamen)
            auxExamen = model_to_dict(auxExamen)
            intentos = intento.objects.filter(idAlumno_id=auxAlumno.id, idExamen_id=idExamen)
            for auxIntento in intentos:
                if auxIntento.estatus=="PENDIENTE":
                    #Devuelve el examen y el avance para mostrarlo en la pantalla
                    preguntas= obtenerPreguntas(idExamen)
                    auxAvances = avances.objects.filter(idIntento_id=auxIntento.id).values()
                    auxAvances = list(auxAvances)
                    auxIntento=model_to_dict(auxIntento)
                    return JsonResponse({'message': "Exito", "intento":auxIntento, "avances": auxAvances, "examen": auxExamen, "preguntas": preguntas})
            nuevoIntento = intento(idExamen_id=idExamen, idAlumno_id=auxAlumno.id, estatus="PENDIENTE", resultado=0)
            nuevoIntento.save()
            nuevoIntento=model_to_dict(nuevoIntento)
            preguntas=obtenerPreguntas(idExamen)
            return JsonResponse({'message': "Exito","intento":nuevoIntento, "avances":[] , "examen": auxExamen, "preguntas": preguntas})
        else:
            return JsonResponse({'message': "Error, debe proporcionar un id"})

    def post(self,request):
        jd=json.loads(request.body)
        idIntento=jd["idIntento"]
        auxIntento=intento.objects.get(id=idIntento)
        resultado=0
        #se leen todas los avances del alumno en el examen
        auxAvances = avances.objects.filter(idIntento_id=idIntento)
        for auxAvance in auxAvances:
            #si la respueta colocada por el alumno es correcta se suma el contador de resultado
            auxRespuesta = respuesta.objects.get(id=auxAvance.idPregunta)
            if auxRespuesta.esCorrecta==True:
                resultado+=1
        #se saca el promedio dividiendo el resultado entre el total de preguntas
        resultado=resultado/auxAvances.count
        auxIntento.resultado=resultado
        auxIntento.estatus="FINALIZADO"
        return JsonResponse({'message': "Exito", 'resultado':resultado})

class API_Avances(View):
    def post (self,request):
        jd=json.loads(request.body)
        idIntento=jd["idIntento"]
        idPregunta = jd["idPregunta"]
        idRespuesta = jd["idRespuesta"]
        auxAvances = avances.objects.filter(idIntento_id=idIntento, idPregunta_id=idPregunta)
        #Valida que haya un avance de ese intento en esa pregunta
        if (auxAvances):
            #se actualiza ese avance
            auxAvances = avances.objects.get(idIntento_id=idIntento, idPregunta_id=idPregunta)
            auxAvances.idRespuesta=idRespuesta
        else:
            #se crea ese avance
            auxAvances = avances(idIntento_id=idIntento, idPregunta_id=idPregunta, idRespuesta_id=idRespuesta)    
        auxAvances.save()
        return JsonResponse({"message": "Exito"})

def obtenerPreguntas(idExamen):
    respuestas_prefetch = Prefetch('respuesta_set', queryset=respuesta.objects.all(), to_attr='respuestas')
    preguntas = pregunta.objects.filter(idExamen_id=idExamen).prefetch_related(respuestas_prefetch) #.order_by("idRama")
    #Las respuestas se deben empalmar aparte para poder devolverlas en un json
    preguntas_list = []
    for auxPregunta in preguntas:
        pregunta_dict = model_to_dict(auxPregunta)
        pregunta_dict['respuestas'] = [model_to_dict(resp) for resp in auxPregunta.respuestas]
        preguntas_list.append(pregunta_dict)
    return preguntas_list