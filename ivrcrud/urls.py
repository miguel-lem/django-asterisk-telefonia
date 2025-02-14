"""
URL configuration for ivrcrud project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
#agregamos el include para que permite incluir rutas creadas en otro archivo y utilizarle desde aqui como si
#de un principio fueran creadas en esta misma ruta 
from django.urls import path,include
#improtamos el static, esta libreria permite que se pueda enviar archivos que no cambian o que 
#pueden cambiar ligeramente, se utiliza para produccion ya que no se esta por lo general utilizando
#en una pc personal ngnx o apache
from django.conf.urls.static import static
#importamos settings que permite acceder a las configuraciones dentro del codigo y darles uso
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    #le colo los urls del otro directorio el de mensajes
    path('api/mensajes/',include('mensajesprojects.urls')),
    #le coloco el otro directorio, el de llamadas
    path('api/llamadas/',include('llamadasproject.urls')), 
    path('api/audios/',include('audiosproject.urls')) 
] #+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
