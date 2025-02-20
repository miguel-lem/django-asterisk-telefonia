from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from asterisk.ami import AMIClient, SimpleAction
#from asterisk.ami.response import FutureResponse
#from rest_framework.test import APIRequestFactory
from audiosproject.views import AudioProcessor
#from rest_framework.request import Request


#en esta clase se realzia una coneccion entre dos extensiones, estas parte realiza la siguiente accion
#llama a la extension 401, luego le conecta la llamada con la 402
class LlamadasViewset(viewsets.ViewSet):
    def event_listener(self, event, **kwargs):
        # Este método se ejecutará cada vez que se reciba un evento
        print("Evento recibido:", event)

    @action(detail=False, methods=['post'])
    def realizar_llamada(self, request):
        # Obtén los parámetros de la solicitud
        channel = request.data.get('channel', '')
        #print("Se esta obteniendo este canal: ",channel)
        exten = request.data.get('exten', '')
        context = request.data.get('context', '')
        priority = request.data.get('priority', 1)
        callerid = request.data.get('callerid', '')

        

        # Validar parámetros obligatorios
        if not channel or not exten:
            return Response({'message': 'Faltan parámetros obligatorios: channel o exten'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Conéctate a Asterisk
            client = AMIClient(address='192.168.2.18',port=5038)
            print("Intentando conectar a Asterisk...")
            # Conexión a Asterisk: Asegúrate de conectar correctamente pasando usuario y contraseña aquí
            client.login(username='admin',secret='mi_contrasenia')
            #client.connect()

            # Añadir el event_listener al cliente
            client.add_event_listener(self.event_listener)

            # Realiza la llamada
            action = SimpleAction(
                'Originate',
                Channel=channel,
                Exten=exten,
                Priority=priority,
                Context=context,
                CallerID=callerid, 
            )
            #client.send_action(action)
            #response = client.send_action(action)
            #print(f"Respuesta AMI: {response}")
            future = client.send_action(action)
            response = future.response
            print(f"Respuesta de Asterisk: {response}")

             # Si la respuesta es una cadena, necesitamos procesarla
            if isinstance(response, str):
                # Convertir la respuesta a un diccionario
                response_dict = {}
                for line in response.split('\r\n'):
                    if line.strip():  # Ignorar líneas vacías
                        key, value = line.split(":", 1)
                        response_dict[key.strip()] = value.strip()

                print("Respuesta procesada:", response_dict)

                # Verificar el resultado
                if response_dict.get('Response') == 'Success':
                    print("Llamada realizada con éxito")
                    return Response({'message': 'Llamada realizada con éxito'})
                else:
                    print("Error al realizar la llamada")
                    return Response({'message': 'Error al realizar la llamada', 'details': response_dict}, status=status.HTTP_400_BAD_REQUEST)

            else:
                print("Respuesta inesperada de Asterisk")
                return Response({'message': 'Respuesta inesperada de Asterisk', 'details': str(response)}, status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            print(f"Error en la conexión a Asterisk: {str(e)}")
            return Response({'message': f'Error en la conexión a Asterisk: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            # Asegúrate de cerrar la conexión correctamente
            try:
                client.logoff()
            except Exception as e:
                print(f"Error al cerrar la conexión: {str(e)}")

#en esta clase se realiza la llamada a la extension 401 y si contesta se le reproduce el audio de hello-world
class LlamadasAudio(viewsets.ViewSet):

    def event_listener(self, event, **kwargs):
        # Este método se ejecutará cada vez que se reciba un evento
        print("Evento recibido:", event)

    @action(detail=False, methods=['post'])
    def play_audio(self, request):
        audio_processor = AudioProcessor() #creo una instancia de la clase donde esta el procesador hacia audio
        print("SE INGRESO A LA FUNCION PARA REPRODUCIR AUDIO") 
        # Obtener el canal de la solicitud
        channel = request.data.get('channel', '')
        if not channel:
            return Response({'status': 'error', 'message': 'El canal no está especificado'}, status=400)
 
        print("Esta es la informacion recibida:", channel)

        try:
            # Conéctate a Asterisk
            client = AMIClient(address='192.168.2.18',port=5038)
            print("Intentando conectar a Asterisk...")
            client.login(username='admin',secret='mi_contrasenia')
            
            # Añadir el event_listener al cliente
            client.add_event_listener(self.event_listener)

            # Realiza la llamada
            action = SimpleAction(
                'Originate',
                Channel=channel, 
                Context='default',  # O el contexto que esta dentro del extensions
                Exten='401',  # Extensión a la que se le genera la llamada
                Priority=1,
                CallerID='Test <401>',
                Application='Playback',  # Usamos Playback para reproducir el audio
                Data= 'hello-world'  # Nombre del archivo de audio que quieres reproducir en Asterisk (debe estar en el directorio adecuado)
            )
            future = client.send_action(action)
            response = future.response
            print(f"Respuesta de Asterisk: {response}")

            # Si la respuesta es una cadena, necesitamos procesarla
            if isinstance(response, str):
                # Convertir la respuesta a un diccionario
                response_dict = {}
                for line in response.split('\r\n'):
                    if line.strip():  # Ignorar líneas vacías
                        key, value = line.split(":", 1)
                        response_dict[key.strip()] = value.strip()

                print("Respuesta procesada:", response_dict)

                # Verificar el resultado
                if response_dict.get('Response') == 'Success':
                    print("Llamada realizada con éxito")
                    return Response({'message': 'Llamada realizada con éxito'})
                else:
                    print("Error al realizar la llamada")
                    return Response({'message': 'Error al realizar la llamada', 'details': response_dict}, status=status.HTTP_400_BAD_REQUEST)

            else:
                print("Respuesta inesperada de Asterisk")
                return Response({'message': 'Respuesta inesperada de Asterisk', 'details': str(response)}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print(f"Error al enviar la acción a Asterisk: {e}")
            return Response({'status': 'error', 'message': f'Error al ejecutar la acción: {e}'}, status=500)
        

#de aqui hacia abajo se esta trabajando en una clase para poder pasarle audios directamente a la llamada 
#el problema esta que el asterisk soporta audios dentro de su servidor
#se esta buscando la manera de poder utilizar un texto a voz y de alli pase directo
import socket


import socket
import time
import requests
import os

class LlamadasEnviarAudio(viewsets.ViewSet):
    
    def event_listener(self, event, **kwargs):
        # Este método se ejecutará cada vez que se reciba un evento
        print("Evento recibido:", event)

    def download_audio(url, filename):
        response = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(response.content)
       '''
       def download_audio(url, temp_audio_path):
    try:
        # Hacer la solicitud GET al archivo de audio en la URL
        response = requests.get(url)
        
        # Verificar que la solicitud fue exitosa
        if response.status_code == 200:
            # Guardar el archivo de audio en el directorio de destino
            with open(temp_audio_path, 'wb') as f:
                f.write(response.content)
            print(f"Archivo descargado y guardado como {temp_audio_path}")
        else:
            print(f"Error al descargar el archivo. Status code: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud: {e}")
       '''     
    @action(detail=False, methods=['post'])
    def play_audio(self, request):
        audio_processor = AudioProcessor()  # Creo una instancia de la clase donde está el procesador hacia audio
        print("SE INGRESO A LA FUNCION PARA REPRODUCIR AUDIO")
        
        # Obtener el canal de la solicitud
        channel = request.data.get('channel', '')
        if not channel:
            return Response({'status': 'error', 'message': 'El canal no está especificado'}, status=400)

        print("Esta es la información recibida:", channel)

        try:
            # Conéctate a Asterisk
            client = AMIClient(address='192.168.2.18', port=5038)
            print("Intentando conectar a Asterisk...")
            client.login(username='admin', secret='mi_contrasenia')

            # Añadir el event_listener al cliente
            client.add_event_listener(self.event_listener)
            #-----esta parte de aqui esta en pruebas
            # URL de donde proviene el archivo de audio
            url = 'http://192.168.2.10:8000/api/audios/crear_audio_get/'
            # Ruta temporal donde se guardará el archivo en Asterisk
            temp_audio_path = '/var/lib/asterisk/sounds/temp_audio.wav'
            # Descargar el archivo de audio
            download_audio(url, temp_audio_path)
            # Realiza la llamada
            action = SimpleAction(
                'Originate',
                Channel=channel,
                Context='default',  # O el contexto que está dentro del extensions
                Exten='401',  # Extensión a la que se le genera la llamada
                Priority=1,
                CallerID='Test <401>',
                Application='StreamFile',  # Usamos StreamFile para reproducir audio desde URL
                Data='temp_audio'  # URL externa del archivo de audio
            )
            #hello-world #http://192.168.2.10:8000/api/audios/crear_audio_get/  /var/lib/asterisk/sounds/mi_audio.wav
            # Eliminar el archivo temporal una vez que se ha reproducido el audio
            os.remove(temp_audio_path)
            future = client.send_action(action)
            response = future.response
            print(f"Respuesta de Asterisk: {response}")

            # Si la respuesta es una cadena, necesitamos procesarla
            if isinstance(response, str):
                # Convertir la respuesta a un diccionario
                response_dict = {}
                for line in response.split('\r\n'):
                    if line.strip():  # Ignorar líneas vacías
                        key, value = line.split(":", 1)
                        response_dict[key.strip()] = value.strip()

                print("Respuesta procesada:", response_dict)

                # Verificar el resultado
                if response_dict.get('Response') == 'Success':
                    print("Llamada realizada con éxito")
                    return Response({'message': 'Llamada realizada con éxito'})
                else:
                    print("Error al realizar la llamada")
                    return Response({'message': 'Error al realizar la llamada', 'details': response_dict}, status=status.HTTP_400_BAD_REQUEST)

            else:
                print("Respuesta inesperada de Asterisk")
                return Response({'message': 'Respuesta inesperada de Asterisk', 'details': str(response)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error al enviar la acción a Asterisk: {e}")
            return Response({'status': 'error', 'message': f'Error al ejecutar la acción: {e}'}, status=500)

