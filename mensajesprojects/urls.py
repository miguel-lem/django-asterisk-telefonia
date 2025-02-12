#importo el routers desde la libreria que permite crear el api rest 
#esta libreria evita tener que crear cada ruta, sino que con una permite en la vista utilizar el CRUD
from rest_framework import routers
#importo la clase ceada para manipular los viewsets en una sola ruta
from mensajesprojects.apy import MensajeViewSet
#creo el objeto de routers
router = routers.DefaultRouter()

#creo la ruta para la navegacion 
router.register('mensajeprincipal',MensajeViewSet,'mensajesprojects')

#le exporto la ruta para poder utilizarle
urlpatterns = router.urls
