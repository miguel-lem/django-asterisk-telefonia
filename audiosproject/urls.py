from audiosproject.views import Audiosviewset
from rest_framework import routers
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

router = routers.DefaultRouter()
router.register(r'audio',Audiosviewset, basename = 'audiosproject')

# Agrega manualmente la acción personalizada
urlpatterns = [ 
    path('escuchar_audio/', Audiosviewset.as_view({'post': 'leer_texto'}), name='leer_texto'),
]

urlpatterns += router.urls

urlpatterns = format_suffix_patterns(urlpatterns)
