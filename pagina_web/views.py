from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from .models import materia, rama
from django.http import JsonResponse
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
        materias = materia.objects.all().order_by("id")
        ramas = rama.objects.all().order_by("id")
        return render(request, 'inicio.html', {'materias': materias, "ramas": ramas})
    
class Logout(View):
    def post(self, request):
        logout(request)
        return redirect('login')
    
def agregar_materia(request):
    if request.method == "POST":
        data = json.loads(request.body)
        nombre = data.get("nombre")
        if nombre:
            nueva_materia = materia(nombre=nombre)
            nueva_materia.save()
            return JsonResponse({"success": True})
        
def agregar_rama(request):
    if request.method == "POST":
        data = json.loads(request.body)
        nombre = data.get("nombre")
        idMateria = data.get("idMateria")
        if nombre:
            nueva_rama = rama(nombre=nombre, idMateria_id=idMateria)
            nueva_rama.save()
            return JsonResponse({"success": True})