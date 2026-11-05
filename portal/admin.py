from django.contrib import admin
from .models import (Amonestacion, Area, Asistencia, Bitacora, Calificacion, Evento, Falta, Horario,
                     Incidencia, Perfil)

for m in (Area, Perfil, Horario, Asistencia, Falta, Incidencia, Amonestacion, Calificacion, Evento, Bitacora):
    admin.site.register(m)
