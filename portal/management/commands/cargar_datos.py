"""Carga datos de prueba ficticios: python manage.py cargar_datos [--reiniciar]"""
import random
from datetime import time, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from portal.models import (Amonestacion, Area, Asistencia, Bitacora, Calificacion, Evento, Falta, Horario,
                           Incidencia, Perfil)

AREAS = ['Dulcería', 'Taquilla', 'Coffee', 'Spiral', 'Salas', 'Limpieza profunda', 'Proyección']

# (número, nombre, apellidos, puesto, áreas, ingreso en días atrás)
COLABORADORES = [
    ('004218', 'Ana', 'López Martínez', 'Cinepolito', ['Dulcería'], 420),
    ('004219', 'Diego', 'Hernández Ruiz', 'Cinepolito', ['Taquilla'], 200),
    ('004225', 'Karla', 'Mendoza Pérez', 'Cinepolito', ['Coffee'], 640),
    ('004231', 'Luis', 'García Torres', 'Cinepolito', ['Salas'], 90),
    ('004236', 'Sofía', 'Vargas León', 'Cinepolito', ['Spiral'], 310),
    ('004243', 'Roberto', 'Pérez Díaz', 'Auxiliar de limpieza', ['Limpieza profunda'], 150),
    ('004245', 'Miguel', 'Torres Rivas', 'Proyeccionista', ['Proyección'], 800),
    ('004252', 'Camila', 'Flores Vega', 'Cinepolito', ['Dulcería'], 60),
    ('004257', 'Mateo', 'Ramírez Soto', 'Cinepolito', ['Dulcería', 'Coffee'], 260),
    ('004261', 'Valeria', 'Cruz Luna', 'Cinepolito', ['Taquilla'], 500),
    ('004268', 'Andrés', 'Salazar Mora', 'Cinepolito', ['Salas'], 35),
    ('004270', 'Regina', 'Ortiz Campos', 'Cinepolito', ['Coffee'], 380),
    ('004274', 'Emilio', 'Navarro Cano', 'Cinepolito', ['Spiral'], 120),
    ('004281', 'Paola', 'Reyes Duarte', 'Cinepolito', ['Taquilla', 'Salas'], 700),
    ('004285', 'Jorge', 'Medina Lara', 'Auxiliar de limpieza', ['Limpieza profunda'], 220),
    ('004290', 'Daniela', 'Aguilar Ponce', 'Proyeccionista', ['Proyección'], 45),
]
TURNOS = [(time(10, 0), time(18, 0)), (time(14, 0), time(22, 0)), (time(12, 0), time(20, 0)),
          (time(16, 0), time(23, 30))]
MOTIVOS_FALTA = ['Enfermedad', 'Asunto familiar', 'Sin aviso', 'Problema de transporte', 'Trámite personal']


class Command(BaseCommand):
    help = 'Carga datos y usuarios de prueba (ficticios).'

    def add_arguments(self, parser):
        parser.add_argument('--reiniciar', action='store_true', help='Borra los datos de prueba antes de cargar.')

    def handle(self, *args, **opciones):
        if opciones['reiniciar']:
            for m in (Bitacora, Evento, Calificacion, Amonestacion, Incidencia, Falta, Asistencia, Horario, Perfil):
                m.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
        if Perfil.objects.exists():
            self.stdout.write('Ya hay datos. Usa --reiniciar para volver a cargarlos.')
            return
        azar = random.Random(2026)
        hoy = timezone.localdate()
        for nombre in AREAS:
            Area.objects.get_or_create(nombre=nombre)
        areas = {a.nombre: a for a in Area.objects.all()}

        def crear(numero, nombre, apellidos, rol, puesto, nombres_area, dias_ingreso, clave):
            u = User.objects.create_user(username=numero, password=clave, first_name=nombre,
                                         last_name=apellidos, email=f'{nombre.lower()}.{numero}@ejemplo.com')
            p = Perfil.objects.create(usuario=u, rol=rol, numero_colaborador=numero, puesto=puesto,
                                      telefono=f'664 555 {azar.randint(1000, 9999)}',
                                      fecha_ingreso=hoy - timedelta(days=dias_ingreso))
            p.areas.set([areas[n] for n in nombres_area])
            return p

        gerente = crear('gerente', 'Mariana', 'Ríos Salgado', Perfil.GERENTE, 'Gerente de conjunto', [], 1500, 'Gerente2026')
        crear('subgerente', 'Fernando', 'Ortega Beltrán', Perfil.SUBGERENTE, 'Subgerente de conjunto', [], 1100, 'Subgerente2026')
        colabs = [crear(n, a, b, Perfil.COLABORADOR, pu, ar, d, 'Cinepolis2026')
                  for n, a, b, pu, ar, d in COLABORADORES]

        # Horarios: 3 semanas (anterior, actual, siguiente); 2 descansos por semana
        lunes = hoy - timedelta(days=hoy.weekday())
        for i, p in enumerate(colabs):
            turno = TURNOS[i % len(TURNOS)]
            area = p.areas.first()
            descansos = {(i + 1) % 7, (i + 4) % 7}
            for semana in (-1, 0, 1):
                for dia in range(7):
                    f = lunes + timedelta(days=7 * semana + dia)
                    if dia in descansos:
                        Horario.objects.create(colaborador=p, area=area, fecha=f, tipo='descanso', asignado_por=gerente.usuario)
                    else:
                        Horario.objects.create(colaborador=p, area=area, fecha=f, hora_entrada=turno[0],
                                               hora_salida=turno[1], asignado_por=gerente.usuario)

        # Asistencias y faltas de los días ya transcurridos (últimas 3 semanas)
        for h in Horario.objects.filter(tipo='turno', fecha__gte=hoy - timedelta(days=21), fecha__lte=hoy):
            suerte = azar.random()
            if h.fecha == hoy and suerte < 0.15:
                continue                                  # aún no llega hoy
            if suerte < 0.05 and h.fecha < hoy:
                Falta.objects.create(colaborador=h.colaborador, fecha=h.fecha, motivo=azar.choice(MOTIVOS_FALTA),
                                     justificada=azar.random() < 0.5, registrada_por=gerente.usuario)
                continue
            retardo = suerte > 0.9
            minutos = azar.randint(8, 25) if retardo else azar.randint(-5, 3)
            entrada = (h.fecha and (timezone.datetime.combine(h.fecha, h.hora_entrada) + timedelta(minutes=minutos)).time())
            Asistencia.objects.create(colaborador=h.colaborador, fecha=h.fecha, hora_entrada=entrada,
                                      hora_salida=None if h.fecha == hoy else h.hora_salida,
                                      estado='retardo' if retardo else 'asistencia', registrada_por=gerente.usuario)

        tipos = ['omision', 'cambio_turno', 'aclaracion', 'salida_anticipada', 'otro']
        descripciones = ['No se registró la salida correspondiente al turno.', 'Solicitó cambio de turno con un compañero.',
                         'Aclaración sobre el registro de entrada del día.', 'Salió antes por indicación del responsable.',
                         'Situación reportada durante la operación del turno.']
        estados = ['pendiente', 'seguimiento', 'resuelta', 'resuelta']
        for i in range(10):
            p = colabs[i % len(colabs)]
            Incidencia.objects.create(colaborador=p, fecha=hoy - timedelta(days=azar.randint(0, 20)),
                                      tipo=tipos[i % 5], descripcion=descripciones[i % 5],
                                      estado=estados[i % 4], registrada_por=gerente.usuario)
        for p, motivo in [(colabs[3], 'Retardos reiterados'), (colabs[1], 'Incumplimiento de procedimiento de cierre'),
                          (colabs[6], 'Uso indebido del uniforme'), (colabs[9], 'Retardos reiterados')]:
            Amonestacion.objects.create(colaborador=p, fecha=hoy - timedelta(days=azar.randint(5, 60)), motivo=motivo,
                                        descripcion='Se le notifica por escrito y se da seguimiento con su responsable de área.',
                                        registrada_por=gerente.usuario)
        comentarios = ['Excelente atención al cliente.', 'Buen trabajo en equipo.', 'Debe mejorar la puntualidad.',
                       'Cumple con sus actividades.', 'Muy buena actitud durante el turno.']
        for p in colabs:
            for k in range(azar.randint(1, 3)):
                Calificacion.objects.create(colaborador=p, estrellas=azar.choice([3, 4, 4, 5, 5]),
                                            comentario=azar.choice(comentarios),
                                            fecha=hoy - timedelta(days=15 * k + 3), calificada_por=gerente.usuario)
        for dias, titulo, desc, area, lugar, hora in [
            (3, 'Reunión general de personal', 'Presentación de la programación del mes.', None, 'Oficinas administrativas', time(11, 0)),
            (8, 'Capacitación de atención al cliente', 'Sesión práctica para el personal de mostrador.', 'Dulcería', 'Sala 5', time(9, 30)),
            (14, 'Convivencia de fin de año', 'Evento para todo el personal de la unidad.', None, 'Lobby', time(17, 0)),
            (20, 'Capacitación de seguridad', 'Protocolos de seguridad y evacuación.', 'Salas', 'Sala 8', time(10, 0)),
        ]:
            Evento.objects.create(titulo=titulo, descripcion=desc, fecha=hoy + timedelta(days=dias),
                                  hora=hora, lugar=lugar, area=areas.get(area), creado_por=gerente.usuario)
        Bitacora.objects.create(usuario=gerente.usuario, accion='Registró', modulo='Sistema',
                                descripcion='Carga inicial de datos de prueba')
        self.stdout.write(self.style.SUCCESS('Datos de prueba cargados.'))
        self.stdout.write('Gerente: gerente / Gerente2026 | Subgerente: subgerente / Subgerente2026')
        self.stdout.write('Colaboradores: 004218 ... 004290 / Cinepolis2026')
