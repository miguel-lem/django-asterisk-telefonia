from audiosproject.views import Audiosviewset
from audiosproject.views import AudioViewSet
from audiosproject.views import AudioViewget
from rest_framework import routers
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

router = routers.DefaultRouter()
router.register(r'audio',Audiosviewset, basename = 'audiosproject')

# Agrega manualmente la acción personalizada
urlpatterns = [ 
    path('escuchar_audio/', Audiosviewset.as_view({'post': 'leer_texto'}), name='leer_texto'),
    path('crear_audio_convertido/', AudioViewSet.as_view({'post': 'convertir_audio'}), name='convertir_audio'),
    path('crear_audio_get/', AudioViewget.as_view({'get': 'convertir_audio'}), name='convertir_audio'),
]

urlpatterns += router.urls

urlpatterns = format_suffix_patterns(urlpatterns)
