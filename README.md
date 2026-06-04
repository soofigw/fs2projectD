# CloudClass (Django)

Proyecto Django tipo plataforma de cursos. Interfaz server-rendered con templates, autenticacion, CRUD de cursos, lecciones y seguimiento de progreso. No incluye API REST (no usa Django REST Framework).

## Caracteristicas

- Catalogo con filtros por texto, categoria y nivel.
- Detalle de curso con inscripcion y porcentaje de avance.
- Lecciones con control de acceso y marcado de progreso.
- Login por correo (backend personalizado) y flujo de password reset.
- Admin Django con modelos registrados.
- Docker + Postgres para despliegue; SQLite como respaldo local.

## Stack

- Python 3.12
- Django 5.x
- PostgreSQL (Docker) / SQLite (local)
- Bootstrap 5 en templates

## Estructura del proyecto

- app/ - configuracion global Django (settings, urls, wsgi, asgi).
- courses/ - app principal con modelos, vistas, forms y templates.
- courses/templates/ - base.html y templates de cursos y autenticacion.
- manage.py - entrypoint de Django.
- Dockerfile, docker-compose.yml - build y orquestacion.
- requirements.txt - dependencias.

## Archivos vitales

- app/settings.py - settings, DB, email, auth backend.
- app/urls.py - rutas globales (admin, auth, courses).
- courses/models.py - CustomUser, Course, Lesson, Enrollment, LessonProgress.
- courses/views.py - logica de negocio (CRUD, inscripcion, progreso).
- courses/urls.py - rutas de cursos y lecciones.
- courses/forms.py - formularios (signup, login, password reset, CRUD).
- courses/backends.py - login por correo.
- courses/admin.py - admin Django.

## Modelo de datos (resumen)

- CustomUser: extiende AbstractUser con email unico.
- Category: agrupa cursos.
- Course: instructor, categoria, nivel, duracion, listado.
- Lesson: contenido por orden (video, texto, imagen, archivo).
- Enrollment: relacion alumno-curso.
- LessonProgress: avance por leccion (completado, fecha, posicion).

## Rutas principales

- / -> catalogo de cursos
- /course/<uuid>/ -> detalle de curso
- /course/<uuid>/enroll/ -> inscripcion
- /course/<uuid>/lesson/<order>/ -> leccion
- /lesson/<id>/toggle-complete/ -> toggle progreso
- /login/, /logout/, /signup/ -> autenticacion
- /password-reset/ -> reset de password
- /admin/ -> panel admin

## Templates

- courses/templates/base.html - layout principal.
- courses/templates/courses/ - catalogo, detalle, leccion.
- courses/templates/registration/ - login, signup, reset.

## Variables de entorno (.env)

- SECRET_KEY
- DEBUG (True/False)
- DB_NAME
- DB_USER
- DB_PASSWORD
- DB_HOST (default: db)
- DB_PORT (default: 5432)
- EMAIL_HOST_USER
- SENDGRID_API_KEY

Ejemplo:

SECRET_KEY=change-me
DEBUG=True
DB_NAME=coursesdb
DB_USER=coursesuser
DB_PASSWORD=coursespass
DB_HOST=db
DB_PORT=5432
EMAIL_HOST_USER=apikey
SENDGRID_API_KEY=your_sendgrid_key

## Ejecutar en local (sin Docker)

1) Crear entorno y activar
2) Instalar dependencias
3) Migrar
4) Correr servidor

Comandos (PowerShell):

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

## Ejecutar con Docker

1) Crear .env en la raiz
2) Levantar contenedores

Comandos:

docker compose up --build

La app queda en http://localhost:8000

## Ejecutar en OCI (Compute + Docker)

1) Crear una instancia en OCI y abrir el puerto 8000 en el NSG o Security List.
2) Instalar Docker y Docker Compose en la VM.
3) Clonar el repositorio y crear el archivo .env.
4) Levantar los contenedores.

Comandos (ejemplo en Ubuntu/Debian):

sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER

git clone <repo>
cd fs2projectD
docker compose up -d --build
docker compose exec web python manage.py migrate

La app queda en http://132.145.136.110:8000

## Tests

python manage.py test

## Notas

- Si no se definen variables DB_*, Django usa SQLite local.
- El backend de login por correo esta en courses/backends.py.
