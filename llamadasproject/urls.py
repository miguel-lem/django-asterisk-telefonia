from rest_framework import routers
from llamadasproject.views import LlamadasViewset
from llamadasproject.views import LlamadasAudio
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

router = routers.DefaultRouter()

#ruta para la navegacion
router.register(r'llamada',LlamadasViewset, basename = 'llamadasproject')

# Agrega manualmente la acción personalizada
urlpatterns = [
    path('realizar_llamada/', LlamadasViewset.as_view({'post': 'realizar_llamada'}), name='realizar_llamada'),
    path('realizar_llamadaunica/', LlamadasAudio.as_view({'post': 'play_audio'}), name='play_audio'),
]

urlpatterns += router.urls

# Si necesitas soporte para los sufijos de formato (json, xml, etc.)
urlpatterns = format_suffix_patterns(urlpatterns)