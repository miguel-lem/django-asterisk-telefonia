#importamos el modelo
from mensajesprojects.models import Mensaje_principalivr
#importamos la libreria que permite ser api rest, viewsets para que permita utilizar las funcionalidades
#de un CRUD dentro de ese modelo, y el permissions para que se pueda controlar que paso le deseo dar
from rest_framework import viewsets,permissions
#importamos el serializador
from mensajesprojects.serializer import MensajeSerializer
from mensajesprojects.serializer import MensajeSerializerId

class MensajeViewSet(viewsets.ModelViewSet):
    queryset = Mensaje_principalivr.objects.all() #creo el query de consulta, en este caso qeu seleccione todo
    permission_classes = [permissions.AllowAny] #le doy todo los permisos, no hay control
    serializer_class = MensajeSerializer #le paso el serializador para con permita el CRUD

#esta funcion se creo para poder comprobar que se puede extraer una campo en especifico 
class MensajeViewSetId(viewsets.ModelViewSet):
    # Obtener solo el 'id' de los registros
    queryset = Mensaje_principalivr.objects.values('mensaje_principal')
    permission_classes = [permissions.AllowAny] 
    serializer_class = MensajeSerializerId 
