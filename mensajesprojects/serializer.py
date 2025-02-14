#de la libreria que permite crear api, le importo el serializer
#esta libreria permite que pueda convertir objetos de python en objetos json o viceversa
from rest_framework import serializers
#importo el modelo creado hace un momento
from mensajesprojects.models import Mensaje_principalivr
class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje_principalivr #aqui inserto el modelo de datos creado
        fields = '__all__'#le digo que lea todos los campos y no le coloco individualmente
        ready_only_fields = ('fecha_ingreso',)

class MensajeSerializerId(serializers.ModelSerializer):
    class Meta:
        model = Mensaje_principalivr #aqui inserto el modelo de datos creado
        fields = ['mensaje_principal']#le digo que lea solo el campo con el nombre
        #ready_only_fields = ('fecha_ingreso',)


