from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import API_Intento, PadronAlumnos, RegistrarAlumno, API_Examen, API_Inicio, Inicio, Login, Logout, RegistrarAlumno, RegistrarUsuario, agregar_examen, agregar_materia, agregar_pregunta, agregar_rama, Examen
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns=[ 
    #URLS de vistas para usarlas desde las templates de DJANGO 
    path('login', Login.as_view(), name='login'),
    path('registrar', RegistrarUsuario.as_view(), name='registrar'),
    path('registrar/alumno', RegistrarAlumno.as_view(), name="registrar_alumno"),
    path('logout', Logout.as_view(), name='logout'),
    path('', Inicio.as_view(), name='inicio'),
    path('examen/<int:id>', Examen.as_view(), name='examen'),
    path('agregar_materia', agregar_materia, name="agregar_materia" ),
    path('agregar_rama', agregar_rama, name="agregar_rama" ),
    path('agregar_examen', agregar_examen, name="agregar_examen"),
    path('agregar_pregunta', agregar_pregunta, name="agregar_pregunta"),
    path('padron/alumnos', PadronAlumnos.as_view(), name='padron_alumnos'),
    
    #URLS de la api para consumirlas desde flutter
    path('api/inicio', API_Inicio.as_view(), name='api_inicio'),
    path('api/examen/<int:id>', API_Examen.as_view(), name='api_examen'),
    path('api/avaces', API_Examen.as_view(), name='api_avances'),
    path('api/intento/<int:idUsuario>/<int:idExamen>', API_Intento.as_view(), name='api_intento'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]