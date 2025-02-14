from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from asterisk.ami import AMIClient, SimpleAction
#from asterisk.ami.response import FutureResponse
#from rest_framework.test import APIRequestFactory
from audiosproject.views import AudioProcessor
#from rest_framework.request import Request


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
            client = AMIClient(address='192.168.227.132',port=5038)
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
            '''
            #creo la variable como none porque en caso al salir de try sin dato tenga uno valor vacio por defecto
            audio_data = None
            # Obtener el contenido binario del archivo de audio
            try:
                #creo la ruta en la que quiero guardar el archivo
                ruta = "C:/Users/mlema/Documents/audios/audio_output.wav"
                #utilizo la clase donde convierto a un audio
                audio_data = audio_processor.texto_a_voz('Este es un texto para probar en la llamada',ruta)
                if audio_data:
                    ruta_convertida = "C:/Users/mlema/Documents/audios/audio_convertido.wav"
                    audio_convertido = audio_processor.convertir_audio(ruta, ruta_convertida)

                    if audio_convertido:
                        print("Audio convertido exitosamente.")
                    else:
                        print("Error al convertir el audio.")
                else:
                    print("Error al generar el audio.")
            except Exception as e:
                return Response({'status': 'error', 'message': f'Error al generar el audio: {e}'}, status=500)

            if not audio_data:
                return Response({'status': 'error', 'message': 'El audio generado es inválido'}, status=500)
            print("Este es el contenido binario del audio:")
            print(audio_data)
            '''
            # Conéctate a Asterisk
            client = AMIClient(address='192.168.227.132',port=5038)
            print("Intentando conectar a Asterisk...")
            client.login(username='admin',secret='mi_contrasenia')
            
            # Añadir el event_listener al cliente
            client.add_event_listener(self.event_listener)

            # Realiza la llamada
            action = SimpleAction(
                'Originate',
                Channel=channel, 
                Context='Long-Distance',  # O el contexto que esta dentro del extensions
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
        
        '''
        # Obtener el contenido binario del archivo de audio
        try:
            audio_data = self.audio_processor.texto_a_voz('Este es un texto para probar en la llamada')
        except Exception as e:
            return Response({'status': 'error', 'message': f'Error al generar el audio: {e}'}, status=500)

        if not audio_data:
            return Response({'status': 'error', 'message': 'El audio generado es inválido'}, status=500)

        # Intentar realizar la llamada a Asterisk
        try:
            response = self.client.send_action({
                'Action': 'PlayTones',
                'Channel': channel,
                'File': audio_data  # Pasamos el contenido binario del archivo de audio
            })
            print("Respuesta de Asterisk:", response)
            return Response({'status': 'success', 'response': response}, status=200)
        
        '''
