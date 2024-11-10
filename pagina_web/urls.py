from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import Inicio, Login, Logout, agregar_examen, agregar_materia, agregar_pregunta, agregar_rama, Examen
urlpatterns=[  
    path('login', Login.as_view(), name='login'),
    path('logout', Logout.as_view(), name='logout'),
    path('', Inicio.as_view(), name='inicio'),
    path('examen/<int:id>', Examen.as_view(), name='examen'),
    path('agregar_materia', agregar_materia, name="agregar_materia" ),
    path('agregar_rama', agregar_rama, name="agregar_rama" ),
    path('agregar_examen', agregar_examen, name="agregar_examen"),
    path('agregar_pregunta', agregar_pregunta, name="agregar_pregunta")
]