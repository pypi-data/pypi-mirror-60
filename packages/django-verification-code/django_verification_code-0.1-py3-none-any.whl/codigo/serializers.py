from rest_framework import serializers


class TelefonoSerializer(serializers.Serializer):
    telefono = serializers.CharField(help_text="telefono a 12 posiciones sin guiones con lada")


class CodigoSerializer(serializers.Serializer):
    codigo = serializers.CharField(help_text="codigo a validar a 5 digitos")
    telefono = serializers.CharField(help_text="telefono a 12 posiciones sin guiones con lada")