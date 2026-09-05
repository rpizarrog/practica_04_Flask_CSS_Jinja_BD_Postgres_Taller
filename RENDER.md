# Despliegue de una aplicación Flask en Render

## PRÁCTICA 04  
### Flask + CSS + Jinja + PostgreSQL + Aiven + Render

---

## 1. Introducción

Durante el desarrollo de una aplicación web con Flask normalmente se ejecuta
el proyecto en la computadora del desarrollador mediante:

```powershell
python app.py
```

Flask proporciona entonces una dirección local similar a:

```text
http://127.0.0.1:5000
```

Esta dirección solamente permite utilizar la aplicación dentro del equipo
donde se está ejecutando Flask.

Para que la aplicación pueda ser utilizada desde Internet es necesario
publicarla en un servidor.

En esta práctica se utilizará **Render** como plataforma de alojamiento de la
aplicación Flask y **Aiven** como servidor PostgreSQL en la nube.

La arquitectura final será:

```text
                    INTERNET
                        │
                        ▼
                 ┌─────────────┐
                 │   RENDER    │
                 │             │
                 │  Gunicorn   │
                 │      │      │
                 │    Flask    │
                 └──────┬──────┘
                        │
                        │ Internet
                        ▼
                 ┌─────────────┐
                 │    AIVEN    │
                 │ PostgreSQL  │
                 └─────────────┘
```

Además, la aplicación utiliza un servidor SMTP para enviar las cotizaciones
por correo electrónico.

---

# 2. Desarrollo local y producción

Es importante distinguir dos ambientes.

## Ambiente de desarrollo

Durante el desarrollo podemos ejecutar:

```text
Navegador
    │
    ▼
Flask
127.0.0.1:5000
    │
    ▼
PostgreSQL LOCAL
localhost:5432
```

También podemos probar desde nuestra computadora la base de datos de Aiven:

```text
Navegador
    │
    ▼
Flask LOCAL
    │
    │ Internet
    ▼
PostgreSQL AIVEN
```

## Ambiente de producción

Cuando Flask se publique en Render:

```text
Usuario
   │
   │ Internet
   ▼
Render
   │
   ▼
Gunicorn
   │
   ▼
Flask
   │
   │ Internet
   ▼
PostgreSQL Aiven
```

En producción ya no se utilizará PostgreSQL instalado en la computadora
del desarrollador.

---

# 3. ¿Por qué Render no puede utilizar nuestro localhost?

Durante el desarrollo tenemos:

```text
DB_LOCAL_HOST=localhost
DB_LOCAL_PORT=5432
```

En nuestra computadora:

```text
localhost
```

significa:

> Esta misma computadora.

Pero cuando Flask se ejecuta en Render:

```text
localhost
```

significa:

> El servidor o contenedor de Render donde se está ejecutando la aplicación.

Por tanto:

```text
Render
   │
   ├── localhost ──► Render
   │
   └── NO ────────► computadora del desarrollador
```

Render no puede utilizar directamente el PostgreSQL instalado en nuestra
computadora mediante `localhost`.

Por esta razón utilizaremos PostgreSQL en Aiven.

---

# 4. Arquitectura de la aplicación

La aplicación está dividida en diferentes componentes.

```text
Usuario
   │
   ▼
Navegador
   │
   │ HTTP / HTTPS
   ▼
app.py
Flask
   │
   ├───────────────┐
   │               │
   ▼               ▼
CPostgreSQL.py   CPDF.py
   │               │
   ▼               ▼
PostgreSQL       ReportLab
Aiven              │
                   ▼
              Documento PDF
                   │
                   ▼
               CCorreo.py
                   │
                   ▼
                 Gmail
                  SMTP
```

Esta separación permite que cada módulo tenga una responsabilidad específica.

### `app.py`

Controla:

- Rutas Flask.
- Formularios.
- Solicitudes HTTP.
- Respuestas HTML.
- Generación de cotizaciones.
- Comunicación entre los diferentes módulos.

### `CPostgreSQL.py`

Controla:

- Conexión a PostgreSQL.
- Registro de clientes.
- Registro de vehículos.
- Registro de solicitudes.
- Consulta de servicios.
- Consulta de solicitudes.
- Registro y consulta de cotizaciones.

### `CPDF.py`

Genera el documento PDF correspondiente a una cotización.

### `CCorreo.py`

Envía la cotización mediante correo electrónico utilizando SMTP.

---

# 5. Estructura del proyecto

La estructura básica del proyecto es:

```text
practica_04_Flask_CSS_Jinja_BD_Postgres_Taller/
│
├── app.py
├── CPostgreSQL.py
├── CPDF.py
├── CCorreo.py
│
├── requirements.txt
├── RENDER.md
├── .gitignore
├── .env
│
├── templates/
│   ├── index.html
│   ├── solicitud_recibida.html
│   ├── solicitudes.html
│   └── cotizacion.html
│
└── static/
    └── css/
        └── estilos.css
```

El archivo `.env` existe en nuestra computadora, pero **NO debe almacenarse
en GitHub**.

---

# 6. Dependencias de Python

Las dependencias necesarias se almacenan en:

```text
requirements.txt
```

Contenido recomendado:

```text
Flask
psycopg2-binary
python-dotenv
reportlab
gunicorn
```

Cada biblioteca cumple una función.

| Biblioteca | Función |
|---|---|
| Flask | Desarrollo de la aplicación web |
| psycopg2-binary | Comunicación con PostgreSQL |
| python-dotenv | Lectura de variables desde `.env` |
| reportlab | Generación de documentos PDF |
| gunicorn | Servidor WSGI para ejecutar Flask en producción |

---

# 7. Flask y Gunicorn

Durante el desarrollo ejecutamos:

```powershell
python app.py
```

Normalmente `app.py` contiene:

```python
if __name__ == "__main__":
    app.run(debug=True)
```

Este servidor es apropiado para desarrollo.

En Render no utilizaremos directamente:

```text
python app.py
```

La aplicación será ejecutada mediante **Gunicorn**:

```text
gunicorn app:app
```

---

# 8. ¿Qué significa `gunicorn app:app`?

Supongamos que tenemos:

```text
app.py
```

y dentro:

```python
from flask import Flask

app = Flask(__name__)
```

El comando:

```text
gunicorn app:app
```

se interpreta como:

```text
gunicorn archivo:objeto
```

Por tanto:

```text
gunicorn app:app
         │   │
         │   └── objeto Flask llamado app
         │
         └────── archivo app.py
```

No se escribe la extensión `.py`.

---

# 9. Archivo `.env`

Durante el desarrollo local utilizamos un archivo:

```text
.env
```

Ejemplo:

```env
# ============================================================
# TIPO DE CONEXIÓN
# ============================================================

TIPO_CONEXION=AIVEN


# ============================================================
# POSTGRESQL LOCAL
# ============================================================

DB_LOCAL_HOST=localhost
DB_LOCAL_PORT=5432
DB_LOCAL_NAME=taller
DB_LOCAL_USER=postgres
DB_LOCAL_PASSWORD=PASSWORD_LOCAL


# ============================================================
# POSTGRESQL AIVEN
# ============================================================

DB_AIVEN_HOST=HOST_AIVEN
DB_AIVEN_PORT=PUERTO_AIVEN
DB_AIVEN_NAME=taller
DB_AIVEN_USER=USUARIO_AIVEN
DB_AIVEN_PASSWORD=PASSWORD_AIVEN


# ============================================================
# CORREO
# ============================================================

CORREO_EMISOR=CORREO_GMAIL
CORREO_PASSWORD=PASSWORD_DE_APLICACION
CORREO_DESTINO_PRUEBA=CORREO_PRUEBA
```

Las credenciales reales no deben escribirse en documentación,
capturas de pantalla ni repositorios públicos.

---

# 10. Selección de la base de datos

En `CPostgreSQL.py` podemos utilizar:

```python
TIPO_CONEXION = os.getenv(
    "TIPO_CONEXION",
    "LOCAL"
).upper()
```

La instrucción:

```python
os.getenv("TIPO_CONEXION", "LOCAL")
```

significa:

> Leer la variable de entorno `TIPO_CONEXION`. Si no existe,
> utilizar `LOCAL`.

Por ejemplo:

```env
TIPO_CONEXION=LOCAL
```

utiliza PostgreSQL local.

Mientras que:

```env
TIPO_CONEXION=AIVEN
```

utiliza PostgreSQL Aiven.

---

# 11. Función general de conexión

La aplicación puede disponer de dos funciones:

```python
def f_conectar_local():
    ...
```

y:

```python
def f_conectar_aiven():
    ...
```

Una función general decide cuál utilizar:

```python
def f_conectar():

    if TIPO_CONEXION == "LOCAL":

        return f_conectar_local()

    elif TIPO_CONEXION == "AIVEN":

        return f_conectar_aiven()

    else:

        raise ValueError(
            "TIPO_CONEXION debe ser LOCAL o AIVEN"
        )
```

Esto permite que el resto de la aplicación simplemente utilice:

```python
conexion = f_conectar()
```

sin preocuparse por dónde se encuentra físicamente PostgreSQL.

---

# 12. Configuración para Render

En Render utilizaremos:

```text
TIPO_CONEXION=AIVEN
```

Por tanto:

```text
Render
   │
   ▼
CPostgreSQL.py
   │
   ▼
f_conectar()
   │
   ▼
TIPO_CONEXION=AIVEN
   │
   ▼
f_conectar_aiven()
   │
   ▼
PostgreSQL Aiven
```

Las variables `DB_LOCAL_*` no son necesarias en Render.

---

# 13. Protección de credenciales

Nunca deben almacenarse directamente en el código instrucciones como:

```python
password = "mi_password_real"
```

Tampoco deben publicarse:

- Contraseñas de PostgreSQL.
- Contraseñas de Aiven.
- Contraseñas de aplicación de Gmail.
- Tokens.
- API Keys.
- Claves privadas.
- Archivos `.env`.

El principio utilizado es:

> El código fuente puede compartirse; las credenciales y secretos
> deben mantenerse separados y protegidos.

---

# 14. Archivo `.gitignore`

El proyecto debe contener:

```text
.gitignore
```

con al menos:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

Esto evita que Git agregue accidentalmente archivos privados o
innecesarios.

Antes de realizar un commit siempre es conveniente ejecutar:

```powershell
git status
```

y verificar que:

```text
.env
```

NO aparezca.

---

# 15. Prueba local antes del despliegue

Antes de publicar la aplicación debemos comprobarla localmente.

Activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Ejecutar:

```powershell
python app.py
```

Abrir:

```text
http://127.0.0.1:5000
```

Comprobar el flujo completo:

1. Mostrar servicios.
2. Registrar una solicitud.
3. Registrar cliente.
4. Registrar vehículo.
5. Consultar solicitudes.
6. Generar cotización.
7. Guardar cotización en PostgreSQL.
8. Generar PDF.
9. Enviar PDF por correo electrónico.

Antes del despliegue conviene realizar esta prueba utilizando:

```env
TIPO_CONEXION=AIVEN
```

De esta manera la aplicación local utiliza la misma base de datos que
utilizará posteriormente Render.

---

# 16. Inicializar Git

Si la carpeta todavía no es un repositorio Git:

```powershell
git init
```

Comprobar:

```powershell
git status
```

Agregar archivos:

```powershell
git add .
```

Comprobar nuevamente:

```powershell
git status
```

Crear commit:

```powershell
git commit -m "Practica 04 Flask PostgreSQL Aiven preparada para Render"
```

---

# 17. Crear repositorio en GitHub

Crear un repositorio en GitHub para almacenar el proyecto.

Después asociar el repositorio local con GitHub.

Ejemplo:

```powershell
git remote add origin URL_DEL_REPOSITORIO
```

Comprobar:

```powershell
git remote -v
```

Configurar la rama principal:

```powershell
git branch -M main
```

Subir:

```powershell
git push -u origin main
```

---

# 18. Verificación en GitHub

Después del `git push`, abrir el repositorio en GitHub.

Deben aparecer archivos como:

```text
app.py
CPostgreSQL.py
CPDF.py
CCorreo.py
requirements.txt
RENDER.md
templates/
static/
```

NO debe aparecer:

```text
.env
```

Si `.env` fue publicado accidentalmente, no basta con eliminarlo posteriormente
del repositorio.

Las credenciales expuestas deben considerarse comprometidas y deben
cambiarse.

---

# 19. Crear el servicio en Render

Ingresar a Render.

Crear:

```text
New
   │
   ▼
Web Service
```

Conectar la cuenta de GitHub y seleccionar el repositorio de la
Práctica 04.

---

# 20. Configuración básica de Render

La configuración será aproximadamente:

```text
Language / Runtime:
Python

Build Command:
pip install -r requirements.txt

Start Command:
gunicorn app:app
```

Render descargará el proyecto desde GitHub e instalará automáticamente
las dependencias.

---

# 21. Build Command

El comando:

```text
pip install -r requirements.txt
```

indica:

> Instalar todas las bibliotecas definidas en `requirements.txt`.

El proceso será aproximadamente:

```text
requirements.txt
       │
       ▼
pip
       │
       ├── Flask
       ├── psycopg2-binary
       ├── python-dotenv
       ├── reportlab
       └── gunicorn
```

---

# 22. Start Command

Después de construir el ambiente, Render ejecutará:

```text
gunicorn app:app
```

El flujo será:

```text
Render
   │
   ▼
Gunicorn
   │
   ▼
app.py
   │
   ▼
app = Flask(__name__)
```

---

# 23. Variables de entorno en Render

El archivo `.env` NO se sube.

En Render deben registrarse las variables de producción.

Por ejemplo:

```text
TIPO_CONEXION=AIVEN

DB_AIVEN_HOST=...
DB_AIVEN_PORT=...
DB_AIVEN_NAME=...
DB_AIVEN_USER=...
DB_AIVEN_PASSWORD=...

CORREO_EMISOR=...
CORREO_PASSWORD=...
```

Si la aplicación utiliza `CORREO_DESTINO_PRUEBA`, también puede
registrarse:

```text
CORREO_DESTINO_PRUEBA=...
```

---

# 24. `.env` local vs variables de Render

Durante el desarrollo:

```text
.env
 │
 ▼
python-dotenv
 │
 ▼
os.getenv()
 │
 ▼
Flask
```

En Render:

```text
Variables de entorno
de Render
       │
       ▼
    os.getenv()
       │
       ▼
      Flask
```

El código Python puede ser exactamente el mismo en ambos ambientes.

---

# 25. ¿Qué ocurre con `load_dotenv()` en Render?

Podemos conservar:

```python
from dotenv import load_dotenv

load_dotenv()
```

En nuestra computadora encuentra:

```text
.env
```

y carga las variables.

En Render no existe el archivo `.env`, pero las variables ya están
definidas en el entorno del servidor.

Posteriormente:

```python
os.getenv("DB_AIVEN_HOST")
```

puede obtenerlas normalmente.

---

# 26. Proceso de despliegue

Cuando Render inicia el despliegue ocurre aproximadamente:

```text
GitHub
   │
   ▼
Render descarga el repositorio
   │
   ▼
Lee requirements.txt
   │
   ▼
Instala dependencias
   │
   ▼
Ejecuta gunicorn app:app
   │
   ▼
Gunicorn carga Flask
   │
   ▼
Flask lee variables de entorno
   │
   ▼
Flask se conecta con Aiven
   │
   ▼
Aplicación disponible en Internet
```

---

# 27. Flujo de una solicitud desde Internet

Una vez desplegada:

```text
Usuario
   │
   │ HTTPS
   ▼
Render
   │
   ▼
Gunicorn
   │
   ▼
Flask
   │
   ▼
Jinja
   │
   ▼
HTML
   │
   ▼
Navegador
```

Cuando el usuario registra información:

```text
Formulario HTML
      │
      ▼
     POST
      │
      ▼
    Flask
      │
      ▼
CPostgreSQL.py
      │
      ▼
PostgreSQL Aiven
```

---

# 28. Flujo de generación de una cotización

```text
Solicitud
    │
    ▼
Flask
    │
    ▼
Consultar PostgreSQL
    │
    ▼
Calcular cotización
    │
    ├───────────────┐
    │               │
    ▼               ▼
PostgreSQL        CPDF.py
    │               │
    │               ▼
    │              PDF
    │               │
    │               ▼
    │           CCorreo.py
    │               │
    │               ▼
    │           Gmail SMTP
    │               │
    ▼               ▼
Cotización       Cliente
almacenada       recibe PDF
```

---

# 29. Base de datos en Aiven

Antes del despliegue debe comprobarse que Aiven contenga las tablas
necesarias:

```text
clientes
vehiculos
servicios
solicitudes
cotizaciones
```

También deben existir los registros correspondientes a los servicios
del taller.

La codificación de PostgreSQL debe manejar correctamente UTF-8 para
almacenar textos como:

```text
Afinación
Diagnóstico
Suspensión
Revisión
Eléctrico
```

---

# 30. Codificación de caracteres

La aplicación utiliza caracteres del idioma español.

Los documentos HTML deben incluir:

```html
<meta charset="UTF-8">
```

PostgreSQL debe utilizar una configuración compatible con UTF-8.

La conexión Python puede establecer:

```python
conexion.set_client_encoding("UTF8")
```

Esto evita problemas con caracteres como:

```text
á
é
í
ó
ú
ñ
```

---

# 31. Correo electrónico

La aplicación utiliza SMTP para enviar la cotización.

Las credenciales del correo se obtienen mediante:

```python
correo_emisor = os.getenv("CORREO_EMISOR")
clave_aplicacion = os.getenv("CORREO_PASSWORD")
```

Nunca deben escribirse directamente dentro de `CCorreo.py`.

En producción Render proporcionará estas variables al proceso de
la aplicación.

---

# 32. Generación de PDF

`CPDF.py` utiliza ReportLab.

El PDF puede generarse en memoria utilizando:

```python
BytesIO
```

Esto es especialmente apropiado en servicios web porque no es necesario
guardar permanentemente cada PDF en el servidor.

El flujo puede ser:

```text
Datos PostgreSQL
      │
      ▼
    Flask
      │
      ▼
  ReportLab
      │
      ▼
   BytesIO
      │
      ├──► navegador
      │
      └──► correo electrónico
```

---

# 33. Archivos en Render

No debe suponerse que los archivos creados localmente en el servidor de
Render funcionarán como almacenamiento permanente.

Los datos importantes de la aplicación deben mantenerse en sistemas
persistentes, por ejemplo:

```text
PostgreSQL Aiven
```

En nuestra aplicación el PDF se genera en memoria, por lo que no dependemos
de almacenamiento permanente para la cotización.

---

# 34. Pruebas después del despliegue

Después de que Render proporcione la dirección pública, comprobar:

```text
Página principal
      │
      ▼
Servicios desde Aiven
      │
      ▼
Nueva solicitud
      │
      ▼
Registro PostgreSQL
      │
      ▼
Listado de solicitudes
      │
      ▼
Cotización
      │
      ▼
Registro de cotización
      │
      ├──► PDF
      │
      └──► Correo
```

Es recomendable realizar una solicitud completa de prueba.

---

# 35. Diagnóstico de errores en Render

Si la aplicación no inicia, revisar primero los **Logs** de Render.

Algunos problemas frecuentes son:

### `ModuleNotFoundError`

Puede indicar que falta una biblioteca en:

```text
requirements.txt
```

### `gunicorn: command not found`

Verificar que exista:

```text
gunicorn
```

en `requirements.txt`.

### Error de conexión PostgreSQL

Revisar:

```text
DB_AIVEN_HOST
DB_AIVEN_PORT
DB_AIVEN_NAME
DB_AIVEN_USER
DB_AIVEN_PASSWORD
```

### La aplicación intenta conectarse a localhost

Revisar:

```text
TIPO_CONEXION=AIVEN
```

### Error al enviar correo

Revisar:

```text
CORREO_EMISOR
CORREO_PASSWORD
```

y las condiciones de autenticación del proveedor de correo.

---

# 36. Actualizaciones posteriores

Una vez conectado Render con GitHub, el flujo de mantenimiento puede ser:

```text
Modificar código
      │
      ▼
Probar localmente
      │
      ▼
git add .
      │
      ▼
git commit
      │
      ▼
git push
      │
      ▼
GitHub
      │
      ▼
Render
      │
      ▼
Nuevo despliegue
```

Por ejemplo:

```powershell
git add .
git commit -m "Actualizar módulo de cotizaciones"
git push
```

Dependiendo de la configuración del servicio, Render puede detectar
el nuevo commit y realizar un nuevo despliegue.

---

# 37. Ambiente de desarrollo vs ambiente de producción

| Característica | Desarrollo | Producción |
|---|---|---|
| Aplicación | Flask local | Flask en Render |
| Servidor | Flask Development Server | Gunicorn |
| Dirección | 127.0.0.1 | Dirección pública HTTPS |
| PostgreSQL | Local o Aiven | Aiven |
| Configuración | `.env` | Variables de Render |
| Código | Git local | GitHub |
| Acceso | Computadora local | Internet |
| PDF | ReportLab | ReportLab |
| Correo | SMTP | SMTP |

---

# 38. Arquitectura final de producción

```text
                        USUARIO
                           │
                           │ HTTPS
                           ▼
                 ┌───────────────────┐
                 │      RENDER       │
                 │                   │
                 │     Gunicorn      │
                 │         │         │
                 │         ▼         │
                 │       Flask       │
                 │         │         │
                 │   Jinja / HTML    │
                 └─────────┬─────────┘
                           │
               ┌───────────┴───────────┐
               │                       │
               ▼                       ▼
      ┌─────────────────┐      ┌────────────────┐
      │      AIVEN      │      │      SMTP      │
      │                 │      │                │
      │   PostgreSQL    │      │     Gmail      │
      │                 │      │                │
      │ clientes        │      │ envío de PDF   │
      │ vehiculos       │      └────────────────┘
      │ servicios       │
      │ solicitudes     │
      │ cotizaciones    │
      └─────────────────┘
```

---

# 39. Resultado esperado

Al finalizar la práctica tendremos una aplicación que:

- Está disponible desde Internet.
- Ejecuta Flask en Render.
- Utiliza Gunicorn como servidor WSGI.
- Utiliza PostgreSQL Aiven como base de datos.
- Mantiene las credenciales fuera del código.
- Genera cotizaciones.
- Almacena las cotizaciones en PostgreSQL.
- Genera documentos PDF.
- Envía cotizaciones por correo electrónico.
- Mantiene el código fuente mediante Git y GitHub.

---

# 40. Conceptos integrados en la práctica

Esta práctica integra diferentes tecnologías y conceptos:

```text
Desarrollo Web
     +
Flask
     +
HTML
     +
CSS
     +
Jinja
     +
PostgreSQL
     +
Base de datos en la nube
     +
Variables de entorno
     +
Seguridad de credenciales
     +
Generación de PDF
     +
Correo SMTP
     +
Git
     +
GitHub
     +
Gunicorn
     +
Render
```

Por tanto, el despliegue no consiste únicamente en "subir una página web".

Se está construyendo una arquitectura donde diferentes servicios cooperan
para ofrecer una aplicación web disponible desde Internet.

---

# 41. Referencias oficiales

Para ampliar la información consultar la documentación oficial de:

- Flask — documentación sobre despliegue en producción.
- Gunicorn — servidor WSGI para aplicaciones Python.
- Render — documentación para despliegue de aplicaciones Flask.
- PostgreSQL — documentación del sistema gestor de bases de datos.
- Psycopg — adaptador PostgreSQL para Python.
- Aiven — documentación de PostgreSQL administrado.
- Python — documentación sobre variables de entorno.
- Git — documentación oficial del sistema de control de versiones.
- GitHub — documentación para repositorios remotos.
- ReportLab — documentación para generación de PDF.

---

## Conclusión

Durante el desarrollo trabajamos principalmente en nuestra computadora:

```text
Flask + PostgreSQL + .env
```

Al llevar la aplicación a producción separamos los componentes:

```text
GitHub
   │
   ▼
Render
   │
   ├── Gunicorn
   │
   └── Flask
          │
          ▼
     PostgreSQL Aiven
```

Las credenciales dejan de almacenarse en archivos compartidos y pasan a
variables de entorno configuradas en el servidor.

Esta arquitectura permite transformar una aplicación Flask desarrollada
localmente en una **aplicación web disponible desde Internet**.