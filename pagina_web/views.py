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
from django.template.loader import render_to_string
from django.db.models import Max, Count

from weasyprint import HTML

import json
import datetime

from .decorators import token_required
from django.utils.decorators import method_decorator

#Clases y funciones para la aplicacion web

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
        # se obtienen todos los alumnos
        alumnos = alumno.objects.all()
        # se construye el json con los datos de cada alumno
        data = []
        for auxAlumno in alumnos:
            intentos = (
                intento.objects.filter(idAlumno=auxAlumno)
                .values("idExamen__id","idExamen__nombre")
                .annotate(
                    cantidad_intentos=Count("idExamen"),
                    calificacion_maxima=Max("resultado"),
                )
            )
            intentos_data = [
                {
                    "id": intento["idExamen__id"],
                    "examen": intento["idExamen__nombre"],
                    "cantidad_intentos": intento["cantidad_intentos"],
                    "calificacion_maxima": intento["calificacion_maxima"],
                }
                for intento in intentos
            ]
            usuarioAlumno = User.objects.get(id=auxAlumno.idUsuario.id)
            # Se agregan los intentos cual el alumno los tiene
            if intentos_data:
                data.append({
                    "id": auxAlumno.id,
                    "nombre": auxAlumno.nombre,
                    "apellido": auxAlumno.apellido,
                    "usuario": usuarioAlumno.username,
                    "intentos": intentos_data,
                })
            else:
                data.append({
                    "id": auxAlumno.id,
                    "nombre": auxAlumno.nombre,
                    "apellido": auxAlumno.apellido,
                    "usuario": usuarioAlumno.username,
                })
        return render(request, 'padron_alumnos.html', {"alumnos":data})

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

class API_Login(View):
    def get(self, request, username, password):
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            return JsonResponse({'message': "Credenciales correctas", 'idusuario': user.id})
        else:
            return JsonResponse({'message': "Credenciales incorrectas"})
 


class API_Inicio(View):
    def get(self, request):
        idUsuario = request.GET.get('user_id')

        try:
            auxAlumno = alumno.objects.get(idUsuario_id=idUsuario)

            examenes = examen.objects.all().values().order_by("id")
            examenes = list(examenes)

            for examenaux in examenes:
                ultimo_intento = intento.objects.filter(
                    idAlumno_id=auxAlumno.id,
                    idExamen_id=examenaux['id'],
                    estatus="FINALIZADO" 
                ).order_by('-id').first()

                if ultimo_intento:
                    examenaux['calificacion'] = ultimo_intento.resultado
                else:
                    examenaux['calificacion'] = 0.0

            return JsonResponse({
                'message': "Bienvenido",
                'examenes': examenes
            })

        except alumno.DoesNotExist:
            return JsonResponse({'message': "Error, el alumno no existe"})

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
        if idUsuario and idExamen:
            try:
                auxAlumno = alumno.objects.get(idUsuario_id=idUsuario)
                auxExamen = examen.objects.get(id=idExamen)
                auxExamen = model_to_dict(auxExamen)

                intento_pendiente = intento.objects.filter(idAlumno_id=auxAlumno.id, idExamen_id=idExamen, estatus="PENDIENTE").first()

                if intento_pendiente:
                    preguntas = obtenerPreguntas(idExamen)
                    auxAvances = avances.objects.filter(idIntento_id=intento_pendiente.id).values()
                    auxAvances = list(auxAvances)
                    intento_pendiente = model_to_dict(intento_pendiente)
                    return JsonResponse({
                        'message': "Exito",
                        "intento": intento_pendiente,
                        "id_intento": intento_pendiente["id"],
                        "avances": auxAvances,
                        "examen": auxExamen,
                        "preguntas": preguntas
                    })

                nuevoIntento = intento(idExamen_id=idExamen, idAlumno_id=auxAlumno.id, estatus="PENDIENTE", resultado=0)
                nuevoIntento.save()
                nuevoIntento = model_to_dict(nuevoIntento)

                preguntas = obtenerPreguntas(idExamen)

                return JsonResponse({
                    'message': "Exito",
                    "intento": nuevoIntento,
                    "id_intento": nuevoIntento["id"],  
                    "avances": [],
                    "examen": auxExamen,
                    "preguntas": preguntas
                })

            except alumno.DoesNotExist:
                return JsonResponse({'message': "Error, el alumno no existe"})
            except examen.DoesNotExist:
                return JsonResponse({'message': "Error, el examen no existe"})
        else:
            return JsonResponse({'message': "Error, debe proporcionar un idUsuario y un idExamen"})

    def post(self, request, idUsuario=0, idExamen=0):

        jd = json.loads(request.body)
        idIntento = jd["idIntento"]

        try:
            auxIntento = intento.objects.get(id=idIntento)
            
            resultado = 0

            auxAvances = avances.objects.filter(idIntento_id=idIntento)
            total_preguntas = auxAvances.count()

            if total_preguntas == 0:
                return JsonResponse({'message': "Error, no hay avances registrados para este intento"}, status=400)

            for auxAvance in auxAvances:
                auxRespuesta = respuesta.objects.get(id=auxAvance.idRespuesta_id)
                if auxRespuesta.esCorrecta:
                    resultado += 1

            resultado = (resultado / total_preguntas)*10
            resultado = round(resultado, 2)

            auxIntento.resultado = resultado
            auxIntento.estatus = "FINALIZADO"
            auxIntento.save()

            return JsonResponse({'message': "Exito", 'resultado': resultado})
        except intento.DoesNotExist:
            return JsonResponse({'message': "Error, el intento no existe"}, status=404)
        except Exception as e:
            return JsonResponse({'message': f"Error inesperado: {str(e)}"}, status=500)


class API_Avances(View):
    
    def post(self, request):

        jd = json.loads(request.body)
        idIntento = jd["idIntento"]
        idPregunta = jd["idPregunta"]
        idRespuesta = jd["idRespuesta"]
        
        auxAvances = avances.objects.filter(idIntento_id=idIntento, idPregunta_id=idPregunta).first()
        
        if auxAvances:
            auxAvances.idRespuesta_id = idRespuesta
        else:
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
        pregunta_dict['nombreRama'] = auxPregunta.idRama.nombre
        pregunta_dict['respuestas'] = [model_to_dict(resp) for resp in auxPregunta.respuestas]
        preguntas_list.append(pregunta_dict)
    return preguntas_list

def generar_reporte(request, idAlumno, idExamen):
    intentos = intento.objects.filter(idAlumno_id=idAlumno, idExamen_id=idExamen)
    listIntentos=[]
    listAvances=[]
    auxExamen = examen.objects.get(id=idExamen)
    respuestas_prefetch = Prefetch('respuesta_set', queryset=respuesta.objects.all(), to_attr='respuestas')
    preguntas = pregunta.objects.filter(idExamen_id=auxExamen.id).prefetch_related(respuestas_prefetch) #.order_by("idRama")
    auxExamen = model_to_dict(auxExamen)
    preguntas=obtenerPreguntas(idExamen)
    auxExamen["preguntas"] = preguntas
    totalPreguntas = len(preguntas)
    for auxIntento in intentos:
            resultado = auxIntento.resultado
            auxAvances = avances.objects.filter(idIntento_id=auxIntento.id).values('id', 'idIntento_id','idPregunta_id','idRespuesta_id', 'idRespuesta__descripcion')
            auxAvances = list(auxAvances)
            auxIntento=model_to_dict(auxIntento)
            auxIntento["totalAciertos"] = round((resultado * totalPreguntas) / 10)
            auxIntento["respuestas"]=auxAvances
            listIntentos.append(auxIntento)
            listAvances.append(auxAvances)
    #return JsonResponse({'message': "Exito","examen": auxExamen, "intentos":listIntentos})
    # Datos de ejemplo
    auxAlumno = alumno.objects.get(id=idAlumno)
    fecha = datetime.date.today().strftime('%d/%m/%Y')
    # Renderizar la plantilla HTML con datos
    html_string = render_to_string('reporte.html', {
        'alumno': model_to_dict(auxAlumno),
        'examen': auxExamen,
        'intentos': listIntentos,
        'fecha': fecha,
    })
    # Crear respuesta en PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'
    HTML(string=html_string).write_pdf(response)
    return response


