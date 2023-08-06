"""Configuración de urls de la app config

Listado de urls para la mayoría de las aplicaciones

"""

from django.urls import path

from codigo.views import EnviarCodigo, VerificaCodigo

urlpatterns = [
    path('enviarCodigo/', EnviarCodigo.as_view(), name='enviar_codigo'),
    path('verificarCodigo/', VerificaCodigo.as_view(), name='verifica_codigo'),
]

