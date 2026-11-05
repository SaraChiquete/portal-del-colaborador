from datetime import timedelta

from django.contrib.auth import views as auth_views  # noqa: F401
from django.db.models import Avg, Q
from django.shortcuts import redirect, render
from django.utils import timezone

from .decorators import solo_colaborador
from .models import Evento, Horario
from .utils import DIAS_LARGO, calcular_logros, dias_semana, fecha_larga, lunes_de, parse_fecha, rango_semana


def inicio(request):
    """Redirige a cada usuario a su vista según su rol."""
    if not request.user.is_authenticated:
        return redirect('login')
    perfil = getattr(request.user, 'perfil', None)
    if perfil is None:
        return redirect('/django-admin/')
    return redirect('panel' if perfil.es_admin else 'portal_inicio')


def _eventos(perfil):
    hoy = timezone.localdate()
    return Evento.objects.filter(fecha__gte=hoy).filter(Q(area__isnull=True) | Q(area__in=perfil.areas.all()))


@solo_colaborador
def portal_inicio(request):
    p = request.user.perfil
    hoy = timezone.localdate()
    inicio_mes = hoy.replace(day=1)
    return render(request, 'portal/colab/inicio.html', {
        'tab': 'inicio', 'p': p, 'fecha': fecha_larga(hoy),
        'turno': p.horarios.filter(fecha=hoy).first(),
        'asistencias': p.asistencias.filter(fecha__gte=inicio_mes, estado='asistencia').count(),
        'retardos': p.asistencias.filter(fecha__gte=inicio_mes, estado='retardo').count(),
        'faltas': p.faltas.filter(fecha__gte=inicio_mes).count(),
        'amonestaciones': p.amonestaciones.count(),
        'logros': calcular_logros(p)[:2], 'eventos': _eventos(p)[:2],
    })


@solo_colaborador
def portal_perfil(request):
    return render(request, 'portal/colab/perfil.html', {'tab': 'perfil', 'p': request.user.perfil})


@solo_colaborador
def portal_horario(request):
    p = request.user.perfil
    lunes = lunes_de(parse_fecha(request.GET.get('semana')))
    mapa = {h.fecha: h for h in p.horarios.filter(fecha__range=(lunes, lunes + timedelta(days=6)))}
    hoy = timezone.localdate()
    dias = [{'fecha': d, 'nombre': DIAS_LARGO[d.weekday()], 'horario': mapa.get(d), 'es_hoy': d == hoy}
            for d in dias_semana(lunes)]
    return render(request, 'portal/colab/horario.html', {
        'tab': 'horario', 'p': p, 'dias': dias, 'rango': rango_semana(lunes),
        'anterior': f'{lunes - timedelta(days=7):%Y-%m-%d}', 'siguiente': f'{lunes + timedelta(days=7):%Y-%m-%d}'})


@solo_colaborador
def portal_faltas(request):
    p = request.user.perfil
    items = [{'titulo': f.motivo, 'fecha': f.fecha, 'texto': '',
              'chip': 'Justificada' if f.justificada else 'Sin justificar',
              'clase': 'verde' if f.justificada else 'rojo'} for f in p.faltas.all()]
    return render(request, 'portal/colab/lista.html', {
        'tab': 'registros', 'titulo': 'Mis faltas', 'subtitulo': 'Faltas registradas y su justificación.',
        'vacio': 'No tienes faltas registradas. ¡Sigue así!', 'items': items})


@solo_colaborador
def portal_amonestaciones(request):
    p = request.user.perfil
    items = [{'titulo': a.motivo, 'fecha': a.fecha, 'texto': a.descripcion, 'chip': '', 'clase': ''}
             for a in p.amonestaciones.all()]
    return render(request, 'portal/colab/lista.html', {
        'tab': 'registros', 'titulo': 'Mis amonestaciones',
        'subtitulo': 'Consulta las amonestaciones registradas a tu nombre.',
        'vacio': 'No tienes amonestaciones registradas.', 'items': items})


@solo_colaborador
def portal_eventos(request):
    items = [{'titulo': e.titulo, 'fecha': e.fecha, 'texto': e.descripcion,
              'chip': e.area.nombre if e.area else 'Todo el personal', 'clase': 'azul',
              'extra': ' · '.join(x for x in (f'{e.hora:%H:%M} h' if e.hora else '', e.lugar) if x)}
             for e in _eventos(request.user.perfil)]
    return render(request, 'portal/colab/lista.html', {
        'tab': 'inicio', 'titulo': 'Eventos', 'subtitulo': 'Próximos eventos de tu unidad.',
        'vacio': 'No hay eventos próximos.', 'items': items})


@solo_colaborador
def portal_logros(request):
    p = request.user.perfil
    promedio = p.calificaciones.aggregate(m=Avg('estrellas'))['m']
    return render(request, 'portal/colab/logros.html', {
        'tab': 'inicio', 'p': p, 'logros': calcular_logros(p), 'promedio': promedio,
        'promedio_texto': f'{promedio:.1f}' if promedio else '',
        'redondeo': round(promedio) if promedio else 0, 'ultima': p.calificaciones.first()})
