from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Prefetch
from django.contrib.auth.models import User
from .models import examen, materia, pregunta, rama, respuesta, alumno
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json

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
    
@method_decorator(staff_member_required(login_url='login'), name='dispatch')
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

class API_CrearUsuario(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)
    
    def post (self,request):
        jd=json.loads(request.body)
        nombre=jd["nombre"]
        apellido=jd["apellido"]
        username = jd["username"]
        email = jd["email"]
        password = jd["email"]
        if User.objects.filter(username=username).exists():
            datos={'message': "Error, ya existe un registro con ese username"}
            return render(request, 'registrar_usuario.html' , {"datos":datos})
        else:
            user = User.objects.create_user(username, email, password)
            user.is_superuser=False
            user.is_staff=False
            user.save()
            nuevoAlumno = alumno(nombre=nombre, apellido=apellido)
            nuevoAlumno.save()
            return redirect("login")