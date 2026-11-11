# Django + Asterisk: Telefonía IVR

API REST construida con Django y Django REST Framework que integra una central telefónica **Asterisk** (vía AMI) para originar llamadas y generar audios de texto a voz (TTS) pensados para un sistema IVR (por ejemplo, cobranza automatizada).

> Estado: prototipo / en desarrollo. Ver la sección [Problemas conocidos](#problemas-conocidos).

## Características

- **Mensajes**: CRUD de mensajes principales del IVR guardados en base de datos.
- **Llamadas**: originar llamadas en Asterisk mediante la interfaz AMI (`Originate`), conectar extensiones y reproducir un audio.
- **Audios**: convertir texto a voz con `pyttsx3` y convertirlo con `ffmpeg` a formato compatible con telefonía (8000 Hz, mono, 16 bits).

## Stack

- Python 3.13, Django 5.1.6, Django REST Framework
- `django-extensions`
- PostgreSQL (configurado en `settings.py`; también hay un `db.sqlite3` en el repo)
- `py-asterisk` (`asterisk.ami`) para AMI
- `pyttsx3`, `numpy`, `requests`
- `ffmpeg` instalado en el sistema (debe estar en el PATH)

## Estructura

```
manage.py
ivrcrud/             Configuración del proyecto (settings, urls raíz)
mensajesprojects/    App de mensajes: modelo, serializers, ViewSets CRUD (apy.py)
llamadasproject/     App de llamadas: integración con Asterisk AMI
audiosproject/       App de audios: texto a voz + conversión con ffmpeg
```

## Modelo de datos

`Mensaje_principalivr` (`mensajesprojects/models.py`):

| Campo               | Tipo               | Notas                    |
|---------------------|--------------------|--------------------------|
| `mensaje_principal` | TextField (300)    | Texto del mensaje        |
| `id_principal`      | IntegerField       | Identificador lógico     |
| `fecha_ingreso`     | DateTimeField      | `auto_now_add`           |

## Endpoints

Todos cuelgan de `ivrcrud/urls.py`.

### Mensajes — `/api/mensajes/`

| Ruta                      | Métodos           | Descripción                                    |
|---------------------------|-------------------|------------------------------------------------|
| `mensajeprincipal/`       | CRUD completo     | CRUD de `Mensaje_principalivr`                 |
| `mensajeprincipalid/`     | CRUD              | Devuelve solo el campo `mensaje_principal`     |

### Llamadas — `/api/llamadas/`

| Ruta                       | Método | Descripción                                                                 |
|----------------------------|--------|-----------------------------------------------------------------------------|
| `realizar_llamada/`        | POST   | `Originate` genérico. Body: `channel`, `exten` (obligatorios), `context`, `priority`, `callerid` |
| `realizar_llamadaunica/`   | POST   | Llama al `channel` indicado y reproduce `hello-world`. Body: `channel`      |
| `realizar_llamadaaudio/`   | POST   | Experimental: descarga el audio TTS y lo reproduce con `StreamFile`         |

Ejemplo:

```bash
curl -X POST http://localhost:8000/api/llamadas/realizar_llamada/ \
  -H "Content-Type: application/json" \
  -d '{"channel": "SIP/401", "exten": "402", "context": "default", "priority": 1, "callerid": "Test <401>"}'
```

### Audios — `/api/audios/`

| Ruta                        | Método | Descripción                                                         |
|-----------------------------|--------|---------------------------------------------------------------------|
| `escuchar_audio/`           | POST   | Body `texto`; devuelve el audio generado (`audio.mp3`)              |
| `crear_audio_convertido/`   | POST   | Body `texto`; devuelve WAV 8 kHz mono 16 bit para Asterisk          |
| `crear_audio_get/`          | GET    | Devuelve un WAV con un texto fijo de prueba (aviso de deuda)        |

## Instalación y ejecución

```bash
python -m venv venv
venv\Scripts\activate            # Windows
pip install django==5.1.6 djangorestframework django-extensions \
            psycopg2-binary py-asterisk pyttsx3 numpy requests

# Instalar ffmpeg y asegurarse de que esté en el PATH

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### Configuración necesaria

Antes de ejecutar, ajusta estos valores que hoy están fijos en el código:

- `ivrcrud/settings.py` → `DATABASES`. Los valores actuales corresponden a una **máquina virtual de pruebas** y **deben reemplazarse** por los de tu propio entorno:

  ```python
  'default': {
      'ENGINE': 'django.db.backends.postgresql',
      'NAME': 'ivruno',            # cambiar: nombre de tu base de datos
      'USER': 'postgres',          # cambiar: usuario de PostgreSQL
      'PASSWORD': 'mi_contrasena', # cambiar: contraseña real (idealmente desde variable de entorno)
      'HOST': '192.168.2.18',      # cambiar: IP/host de tu servidor PostgreSQL
      'PORT': '5432'
  }
  ```

  Para pruebas locales puedes usar SQLite.
- `llamadasproject/views.py` → dirección AMI de Asterisk (`192.168.2.18:5038`) y credenciales.
- `audiosproject/views.py` → ruta de salida `C:/Users/mlema/Documents/audios/` en `convertir_audio`.

En Asterisk, habilita AMI en `manager.conf` con un usuario que tenga permisos `originate`, y define el contexto/extensiones (`default`, 401, 402) usados en los ejemplos.

## Problemas conocidos

Hallazgos del análisis del código:

1. **`llamadasproject/views.py` no se puede importar**: hay un bloque `'''...'''` mal indentado (línea ~188) justo después de `download_audio`, lo que provoca `SyntaxError` y rompe todo el proyecto al cargar las URLs.
2. **`LlamadasEnviarAudio`**: `download_audio` no tiene `self` y se llama sin él; además borra el archivo temporal (`os.remove`) *antes* de enviar el `Originate`, y escribe en una ruta de Asterisk (`/var/lib/asterisk/sounds`) que no existe en el servidor Django salvo que sea la misma máquina. Además hace una petición HTTP a su propio servidor.
3. **`AudioProcessor.convertir_audio`**: ffmpeg escribe en `nueva_ruta` (nombre aleatorio) pero luego lee `output_path` (nombre fijo), por lo que falla o devuelve un archivo antiguo. Tampoco usa `-y`, y la ruta es de una máquina Windows concreta.
4. **Seguridad**: `SECRET_KEY`, contraseña de PostgreSQL y credenciales AMI están en el código; `DEBUG = True`, `ALLOWED_HOSTS = ['*']` y los endpoints usan `AllowAny` sin autenticación. Cualquiera con acceso a la red podría originar llamadas. Se recomienda mover los secretos a variables de entorno y proteger la API.
5. `MensajeSerializer` usa `ready_only_fields` (typo de `read_only_fields`), así que `fecha_ingreso` no queda realmente como solo lectura.
6. `escuchar_audio` guarda con extensión `.mp3` pero `pyttsx3` genera WAV; además usa un archivo `output.mp3` compartido (condición de carrera con peticiones concurrentes).
7. El texto de `crear_audio_get` está fijo en el código; el cliente `AMIClient` se conecta y desconecta por cada petición.
8. El repo incluye `__pycache__`, `db.sqlite3` y un archivo vacío `ivruno`; faltan `requirements.txt` y `.gitignore`. Los modelos de `llamadasproject` y `audiosproject` están vacíos (no hay registro de llamadas).
9. `mensajesprojects/apy.py` probablemente quiso llamarse `api.py`.

## Ideas de mejora

- Registrar cada llamada en un modelo (estado, destino, fecha, resultado).
- Generar el audio TTS y colocarlo en el directorio de sonidos de Asterisk (o usar AGI/ARI), en lugar de descargarlo por HTTP.
- Procesar el texto del mensaje desde la base de datos (`Mensaje_principalivr`) en lugar de texto fijo.
- Autenticación (token/JWT), variables de entorno (`python-decouple` o `django-environ`) y tests.
