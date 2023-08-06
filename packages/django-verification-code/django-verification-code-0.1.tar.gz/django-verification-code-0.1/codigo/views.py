from random import randint

from django.contrib.auth import get_user_model
from django.shortcuts import render

from django.conf import settings

# Create your views here.
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.rest import Client

from codigo.models import Codigo
from codigo.serializers import TelefonoSerializer, CodigoSerializer


def enviar_codigo(telefono):
    account_sid = settings.TWILIO_SID
    auth_token = settings.TWILIO_TOKEN
    client = Client(account_sid, auth_token)
    cs = Codigo.objects.filter(telefono=telefono)
    cs.delete()
    codigo = randint(1, 99999)
    codigo = "{0:0=5d}".format(codigo)
    c = Codigo(codigo=codigo, telefono=telefono)
    c.save()
    telefono = "+" + telefono
    try:
        message = client.messages.create(
            to=telefono,
            from_=settings.TWILIO_NUMBER,
            body="Tu número de verificación  es " + str(codigo))
        return True
    except Exception as e:
        return False


class EnviarCodigo(APIView):
    """
    post:
    Envia un codigo sms al telefono
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TelefonoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if enviar_codigo(serializer.validated_data.get('telefono')):
            return Response({'result': 1}, status=status.HTTP_200_OK)
        else:
            return Response({'result': 0, 'errores': serializer.errors}, status=status.HTTP_424_FAILED_DEPENDENCY)

    def get_serializer(self):
        return TelefonoSerializer()


class VerificaCodigo(APIView):
    """
        post:
        Verifica el codigo enviado y regresa el result
        0 no hay usuario
        -1 el codigo es inválido
        1 si hya usuarioy regresa token
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        response_data = {}
        serializer = CodigoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        telefono = vd.get('telefono')
        codigo = vd.get('codigo')
        cs = Codigo.objects.filter(telefono=telefono, codigo=codigo)
        if cs.exists():
            if get_user_model().objects.filter(telefono=telefono).exists():
                u = get_user_model().objects.get(telefono=telefono)
                cs.delete()
                response_data = {'result': 1, "pk": u.pk}
            else:
                response_data['result'] = 0
        else:
            response_data['result'] = -1
        return Response(response_data, status=status.HTTP_200_OK)

    def get_serializer(self):
        return CodigoSerializer()
