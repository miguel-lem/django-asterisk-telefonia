from django.shortcuts import render
from rest_framework import viewsets
from django.http import HttpResponse
import pyttsx3
import os
#import wave
import numpy as np
import subprocess

from rest_framework.decorators import action

class Audiosviewset(viewsets.ViewSet):
    
    def leer_texto(self,request):
        # Verificamos si la solicitud es POST y si el parámetro "texto" está presente
        if request.method == 'POST':
            texto = request.data.get('texto', '')
            #texto = request.POST.get('texto', 'Texto no proporcionado.')
        else:
            texto = 'Método no permitido, por favor usa POST.'
        
        # Inicializar pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1)

        # Generar el audio
        engine.save_to_file(texto, 'output.mp3')
        engine.runAndWait()

        # Enviar el archivo como respuesta
        with open('output.mp3', 'rb') as f:
            response = HttpResponse(f.read(), content_type="audio/mp3")
            response['Content-Disposition'] = 'attachment; filename="audio.mp3"'
            return response


#esta clase es una normal en base a la de arriba para poder utilizarla dentro de otra clase
#sin necesidad de generar el json

class AudioProcessor:
    def __init__(self):
        # Aquí puedes inicializar cualquier parámetro o configuraciones que necesites.
        pass

    def texto_a_voz(self,texto,ruta_destino):
        # Inicializar pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1)

        # Generar el audio en formato .wav
        temp_audio_path = 'output.wav'
        engine.save_to_file(texto, temp_audio_path)
        engine.runAndWait()
        # Se dice al sistema operativo que guarde en la ruta
        os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
        try:
            # Genero el archivo de audio en formato .wav y guardo en la ruta
            engine.save_to_file(texto, ruta_destino)
            engine.runAndWait()
            print(f"Archivo de audio guardado en: {ruta_destino}")

            with open(temp_audio_path, 'rb') as f:
                audio_binario = f.read()
        except Exception as e:
            print(f"Error al leer el archivo .wav: {e}")
            return None
        
        # Eliminar los archivos temporales
        os.remove(temp_audio_path)

        return audio_binario
    
    def convertir_audio(self,input_path, output_path):
        try:
            # Usamos ffmpeg para convertir el archivo generado a las especificaciones requeridas
            # Comando ffmpeg para convertir a 8000Hz, Mono y 16 bits
            subprocess.run([
                'ffmpeg', '-i', input_path,  # archivo de entrada
                '-ar', '8000',               # establecer la tasa de muestreo a 8000Hz
                '-ac', '1',                  # convertir a mono (1 canal)
                '-sample_fmt', 's16',        # establecer a 16 bits (sample format s16)
                output_path                  # archivo de salida
            ], check=True)

            print(f"Archivo de audio convertido y guardado en: {output_path}")

            # Leer el archivo de audio convertido como binario
            with open(output_path, 'rb') as f:
                audio_binario = f.read()

        except Exception as e:
            print(f"Error al convertir el archivo con ffmpeg: {e}")
            return None

        return audio_binario


