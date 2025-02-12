from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from asterisk.ami import AMIClient, SimpleAction
from asterisk.ami.response import FutureResponse

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
        context = request.data.get('context', 'Long-Distance')
        priority = request.data.get('priority', 1)
        callerid = request.data.get('callerid', 'Mi llamada')

        

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