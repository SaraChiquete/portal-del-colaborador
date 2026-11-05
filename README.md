# Portal del Colaborador · Cinépolis Sendero Tijuana

Sistema web de gestión y seguimiento de colaboradores (Python, Django, HTML, CSS, JavaScript, MariaDB/MySQL).

## Puesta en marcha en Windows (XAMPP)

1. Abre XAMPP e inicia **MySQL**. En `http://localhost/phpmyadmin` (pestaña SQL) ejecuta:

   ```sql
   CREATE DATABASE portal_colaborador CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. En una terminal, dentro de la carpeta del proyecto:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py cargar_datos
   python manage.py runserver
   ```

   Si `pip install mysqlclient` falla, ejecuta `pip install pymysql` (el proyecto lo detecta solo).

3. Abre `http://127.0.0.1:8000`.

Si tu MySQL tiene contraseña para `root`, edita el bloque `DATABASES` de `config/settings.py`.

## Usuarios de prueba

| Rol | Usuario | Contraseña |
|---|---|---|
| Gerente | `gerente` | `Gerente2026` |
| Subgerente | `subgerente` | `Subgerente2026` |
| Colaborador | `004218` (Ana López, Dulcería) | `Cinepolis2026` |
| Colaborador | `004219` (Diego Hernández, Taquilla) | `Cinepolis2026` |
| Colaborador | `004225` … `004290` (16 en total) | `Cinepolis2026` |

Para volver a cargar los datos de prueba desde cero: `python manage.py cargar_datos --reiniciar`.

## Pruebas automáticas

```bash
python manage.py test portal
```

## Scripts SQL (carpeta `database/`)

- `schema.sql`: crea la base de datos y todas las tablas.
- `datos_prueba.sql`: datos de prueba (incluye el historial de migraciones de Django).
- `modelo_er.md`: modelo entidad-relación y modelo relacional.

Alternativa sin `migrate`: importa `schema.sql` y luego `datos_prueba.sql` en phpMyAdmin.
Usa un solo camino (migraciones **o** scripts), no ambos sobre la misma base.

## Estructura

```
config/            configuración de Django
portal/models.py   tablas de la base de datos
portal/views_admin.py    panel de gerente y subgerente
portal/views_portal.py   portal del colaborador (celular)
portal/forms.py, utils.py, decorators.py, urls.py
portal/templates/  pantallas HTML (admin/ y colab/)
portal/static/     CSS y JavaScript
portal/management/commands/cargar_datos.py   datos de prueba
database/          scripts SQL y modelo de datos
```

## Qué cubre (según la tesina)

- **Gerente y subgerente (misma vista):** consultar colaboradores, asignar horarios por área/día/hora con casillas,
  registrar asistencias, faltas, incidencias y amonestaciones, calificar con estrellas (1 a 5), eventos, bitácora
  de acciones y descarga de horarios en PDF.
- **Colaborador ("cinepolito"):** solo su información: datos básicos, horario, faltas, amonestaciones, eventos y logros.
- **Áreas:** Dulcería, Taquilla, Coffee, Spiral, Salas, Limpieza profunda y Proyección.
