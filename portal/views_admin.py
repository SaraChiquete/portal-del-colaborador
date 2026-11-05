from datetime import datetime, timedelta

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .decorators import solo_admin
from .forms import (AmonestacionForm, AsistenciaForm, CalificacionForm, ColaboradorForm, EventoForm,
                    FaltaForm, IncidenciaForm)
from .models import (Amonestacion, Area, Asistencia, Bitacora, Calificacion, Evento, Falta, Horario,
                     Incidencia, Perfil)
from .utils import (DIAS_CORTO, dias_semana, fecha_larga, lunes_de, parse_fecha, pdf_horarios,
                    rango_semana, registrar_bitacora)

COLABORADORES = Perfil.objects.filter(rol=Perfil.COLABORADOR).select_related('usuario').prefetch_related('areas')


# ------------------------------------------------------------------ Panel
@solo_admin
def dashboard(request):
    hoy = timezone.localdate()
    inicio_mes = hoy.replace(day=1)
    lunes = lunes_de(hoy)
    semana = []
    for d in dias_semana(lunes):
        programados = Horario.objects.filter(fecha=d, tipo=Horario.TURNO).count()
        asistieron = Asistencia.objects.filter(fecha=d).count()
        pct = round(asistieron * 100 / programados) if programados else 0
        semana.append({'dia': DIAS_CORTO[d.weekday()], 'pct': pct, 'es_hoy': d == hoy,
                       'futuro': d > hoy, 'asistieron': asistieron, 'programados': programados})
    por_area = [{'nombre': a.nombre,
                 'total': Horario.objects.filter(fecha=hoy, area=a, tipo=Horario.TURNO).count()}
                for a in Area.objects.all()]
    maximo = max([x['total'] for x in por_area] + [1])
    for x in por_area:
        x['pct'] = round(x['total'] * 100 / maximo)
    contexto = {
        'seccion': 'panel', 'hoy': fecha_larga(hoy),
        'activos': COLABORADORES.filter(activo=True).count(),
        'asistencias_hoy': Asistencia.objects.filter(fecha=hoy).count(),
        'programados_hoy': Horario.objects.filter(fecha=hoy, tipo=Horario.TURNO).count(),
        'faltas_mes': Falta.objects.filter(fecha__gte=inicio_mes).count(),
        'retardos_mes': Asistencia.objects.filter(fecha__gte=inicio_mes, estado='retardo').count(),
        'incidencias_pendientes': Incidencia.objects.exclude(estado=Incidencia.RESUELTA).count(),
        'semana': semana, 'por_area': por_area,
        'pendientes': Incidencia.objects.exclude(estado=Incidencia.RESUELTA).select_related('colaborador__usuario')[:5],
    }
    return render(request, 'portal/admin/dashboard.html', contexto)


# ----------------------------------------------------------- Colaboradores
@solo_admin
def colaboradores(request):
    qs = COLABORADORES
    q = request.GET.get('q', '').strip()
    area = request.GET.get('area', '')
    if q:
        qs = qs.filter(Q(usuario__first_name__icontains=q) | Q(usuario__last_name__icontains=q)
                       | Q(numero_colaborador__icontains=q))
    if area.isdigit():
        qs = qs.filter(areas__id=area)
    return render(request, 'portal/admin/colaboradores.html', {
        'seccion': 'colaboradores', 'lista': qs.distinct(), 'areas': Area.objects.all(), 'q': q, 'area': area})


@solo_admin
def colaborador_form(request, pk=None):
    perfil = get_object_or_404(COLABORADORES, pk=pk) if pk else None
    form = ColaboradorForm(request.POST or None, perfil=perfil)
    if request.method == 'POST' and form.is_valid():
        nuevo = form.guardar()
        registrar_bitacora(request.user, 'Editó' if perfil else 'Registró', 'Colaboradores', nuevo.nombre_completo)
        messages.success(request, 'Colaborador guardado correctamente.')
        return redirect('colaborador_detalle', pk=nuevo.pk)
    return render(request, 'portal/admin/colaborador_form.html', {
        'seccion': 'colaboradores', 'form': form, 'perfil': perfil})


@solo_admin
def colaborador_detalle(request, pk):
    p = get_object_or_404(COLABORADORES, pk=pk)
    hoy = timezone.localdate()
    lunes = lunes_de(hoy)
    horarios = {h.fecha: h for h in p.horarios.filter(fecha__range=(lunes, lunes + timedelta(days=6)))}
    semana = [{'dia': DIAS_CORTO[d.weekday()], 'fecha': d, 'horario': horarios.get(d)} for d in dias_semana(lunes)]
    return render(request, 'portal/admin/colaborador_detalle.html', {
        'seccion': 'colaboradores', 'p': p, 'semana': semana, 'rango': rango_semana(lunes),
        'asistencias': p.asistencias.all()[:6], 'faltas': p.faltas.all()[:5],
        'incidencias': p.incidencias.all()[:5], 'amonestaciones': p.amonestaciones.all()[:5],
        'calificaciones': p.calificaciones.all()[:5],
        'promedio': p.calificaciones.aggregate(m=Avg('estrellas'))['m'],
        'form_cal': CalificacionForm(initial={'estrellas': 5}),
    })


@solo_admin
@require_POST
def calificar(request, pk):
    p = get_object_or_404(COLABORADORES, pk=pk)
    form = CalificacionForm(request.POST)
    if form.is_valid():
        c = form.save(commit=False)
        c.colaborador, c.fecha, c.calificada_por = p, timezone.localdate(), request.user
        c.save()
        registrar_bitacora(request.user, 'Calificó', 'Desempeño', f'{p.nombre_completo}: {c.estrellas} estrellas')
        messages.success(request, 'Calificación registrada.')
    else:
        messages.error(request, 'Selecciona una calificación de 1 a 5 estrellas.')
    return redirect('colaborador_detalle', pk=p.pk)


# ---------------------------------------------------------------- Horarios
def _datos_semana(area, lunes):
    fin = lunes + timedelta(days=6)
    horarios = Horario.objects.filter(area=area, fecha__range=(lunes, fin)).select_related('colaborador__usuario')
    ids = set(area.colaboradores.filter(rol=Perfil.COLABORADOR, activo=True).values_list('id', flat=True))
    ids |= {h.colaborador_id for h in horarios}
    mapa = {(h.colaborador_id, h.fecha): h for h in horarios}
    filas = []
    for p in Perfil.objects.filter(id__in=ids).select_related('usuario'):
        filas.append({'perfil': p, 'celdas': [mapa.get((p.id, d)) for d in dias_semana(lunes)]})
    return filas


def _area_y_semana(request):
    areas = list(Area.objects.all())
    area = next((a for a in areas if str(a.id) == request.GET.get('area')), areas[0])
    return areas, area, lunes_de(parse_fecha(request.GET.get('semana')))


@solo_admin
def horarios(request):
    areas, area, lunes = _area_y_semana(request)
    dias = dias_semana(lunes)
    destino = f"{request.path}?area={area.id}&semana={lunes:%Y-%m-%d}"
    if request.method == 'POST':
        ids = request.POST.getlist('colaboradores')
        fechas = [parse_fecha(f) for f in request.POST.getlist('dias')]
        tipo = request.POST.get('tipo', Horario.TURNO)
        try:
            entrada = datetime.strptime(request.POST.get('hora_entrada', ''), '%H:%M').time()
            salida = datetime.strptime(request.POST.get('hora_salida', ''), '%H:%M').time()
        except ValueError:
            entrada = salida = None
        if not ids or not fechas:
            messages.error(request, 'Selecciona al menos un colaborador y un día.')
        elif tipo == Horario.TURNO and (not entrada or not salida or entrada == salida):
            messages.error(request, 'Indica una hora de entrada y de salida distintas.')
        else:
            if tipo == Horario.DESCANSO:
                entrada = salida = None
            seleccion = Perfil.objects.filter(id__in=ids, rol=Perfil.COLABORADOR)
            for p in seleccion:
                for f in fechas:
                    Horario.objects.update_or_create(colaborador=p, fecha=f, defaults={
                        'area': area, 'tipo': tipo, 'hora_entrada': entrada, 'hora_salida': salida,
                        'asignado_por': request.user})
            texto = 'descanso' if tipo == Horario.DESCANSO else f'{entrada:%H:%M}-{salida:%H:%M}'
            registrar_bitacora(request.user, 'Asignó', 'Horarios',
                               f'{texto} a {seleccion.count()} colaborador(es) en {area.nombre}, {len(fechas)} día(s)')
            messages.success(request, 'Horario asignado correctamente.')
        return redirect(destino)
    return render(request, 'portal/admin/horarios.html', {
        'seccion': 'horarios', 'areas': areas, 'area': area, 'lunes': lunes, 'rango': rango_semana(lunes),
        'dias': [{'fecha': d, 'etiqueta': DIAS_CORTO[d.weekday()]} for d in dias],
        'filas': _datos_semana(area, lunes),
        'candidatos': area.colaboradores.filter(rol=Perfil.COLABORADOR, activo=True).select_related('usuario'),
        'anterior': f'{lunes - timedelta(days=7):%Y-%m-%d}', 'siguiente': f'{lunes + timedelta(days=7):%Y-%m-%d}',
        'hoy': f'{timezone.localdate():%Y-%m-%d}',
    })


@solo_admin
def horarios_pdf(request):
    _, area, lunes = _area_y_semana(request)
    filas = [(f['perfil'].nombre_completo, f['celdas']) for f in _datos_semana(area, lunes)]
    registrar_bitacora(request.user, 'Descargó', 'Horarios', f'PDF de {area.nombre}, semana {lunes:%d/%m/%Y}')
    respuesta = HttpResponse(pdf_horarios(area, lunes, filas), content_type='application/pdf')
    respuesta['Content-Disposition'] = f'attachment; filename="horario_{area.nombre}_{lunes:%Y%m%d}.pdf"'
    return respuesta


@solo_admin
@require_POST
def horario_eliminar(request, pk):
    h = get_object_or_404(Horario, pk=pk)
    registrar_bitacora(request.user, 'Eliminó', 'Horarios', str(h))
    h.delete()
    messages.success(request, 'Horario eliminado.')
    return redirect(request.META.get('HTTP_REFERER') or 'horarios')


# --------------------------------------- Registros (asistencias, faltas...)
REGISTROS = {
    'asistencias': dict(modelo=Asistencia, form=AsistenciaForm, titulo='Asistencias y retardos',
                        singular='asistencia', modulo='Asistencias',
                        columnas=[('Fecha', 'fecha'), ('Colaborador', 'colaborador'), ('Entrada', 'hora_entrada'),
                                  ('Salida', 'hora_salida'), ('Estado', 'estado', True)]),
    'faltas': dict(modelo=Falta, form=FaltaForm, titulo='Faltas', singular='falta', modulo='Faltas',
                   columnas=[('Fecha', 'fecha'), ('Colaborador', 'colaborador'), ('Motivo', 'motivo'),
                             ('Justificada', 'justificada', True)]),
    'incidencias': dict(modelo=Incidencia, form=IncidenciaForm, titulo='Incidencias', singular='incidencia',
                        modulo='Incidencias',
                        columnas=[('Fecha', 'fecha'), ('Colaborador', 'colaborador'), ('Tipo', 'tipo'),
                                  ('Descripción', 'descripcion'), ('Estado', 'estado', True)]),
    'amonestaciones': dict(modelo=Amonestacion, form=AmonestacionForm, titulo='Amonestaciones',
                           singular='amonestación', modulo='Amonestaciones',
                           columnas=[('Fecha', 'fecha'), ('Colaborador', 'colaborador'), ('Motivo', 'motivo'),
                                     ('Registrada por', 'registrada_por')]),
    'eventos': dict(modelo=Evento, form=EventoForm, titulo='Eventos', singular='evento', modulo='Eventos',
                    columnas=[('Fecha', 'fecha'), ('Evento', 'titulo'), ('Hora', 'hora'), ('Lugar', 'lugar'),
                              ('Área', 'area')]),
}
CHIPS = {'Pendiente': 'amarillo', 'En seguimiento': 'azul', 'Resuelta': 'verde', 'Retardo': 'amarillo',
         'Asistencia': 'verde', 'Sí': 'verde', 'No': 'rojo'}


def _config(clave):
    if clave not in REGISTROS:
        raise Http404
    return REGISTROS[clave]


def _valor(obj, atributo):
    if hasattr(obj, f'get_{atributo}_display'):
        return getattr(obj, f'get_{atributo}_display')()
    v = getattr(obj, atributo)
    if v is None or v == '':
        return '—'
    if hasattr(v, 'strftime'):
        return v.strftime('%d/%m/%Y' if hasattr(v, 'year') else '%H:%M')
    if isinstance(v, bool):
        return 'Sí' if v else 'No'
    if atributo == 'registrada_por':
        return v.get_full_name() or v.username
    return str(v.nombre_completo if hasattr(v, 'nombre_completo') else v)


@solo_admin
def registro_lista(request, clave):
    c = _config(clave)
    qs = c['modelo'].objects.all()
    if hasattr(c['modelo'], 'colaborador'):
        qs = qs.select_related('colaborador__usuario')
    q = request.GET.get('q', '').strip()
    if q:
        if clave == 'eventos':
            qs = qs.filter(titulo__icontains=q)
        else:
            qs = qs.filter(Q(colaborador__usuario__first_name__icontains=q)
                           | Q(colaborador__usuario__last_name__icontains=q)
                           | Q(colaborador__numero_colaborador__icontains=q))
    desde, hasta = request.GET.get('desde'), request.GET.get('hasta')
    if desde:
        qs = qs.filter(fecha__gte=parse_fecha(desde))
    if hasta:
        qs = qs.filter(fecha__lte=parse_fecha(hasta))
    pagina = Paginator(qs, 12).get_page(request.GET.get('page'))
    filas = []
    for obj in pagina:
        celdas = []
        for col in c['columnas']:
            texto = _valor(obj, col[1])
            celdas.append({'t': texto, 'c': CHIPS.get(texto, '') if len(col) > 2 else ''})
        filas.append({'pk': obj.pk, 'celdas': celdas})
    parametros = request.GET.copy()
    parametros.pop('page', None)
    return render(request, 'portal/admin/lista.html', {
        'seccion': clave, 'clave': clave, 'c': c, 'pagina': pagina, 'filas': filas,
        'encabezados': [col[0] for col in c['columnas']], 'q': q, 'desde': desde or '', 'hasta': hasta or '',
        'qs': parametros.urlencode()})


@solo_admin
def registro_form(request, clave, pk=None):
    c = _config(clave)
    obj = get_object_or_404(c['modelo'], pk=pk) if pk else None
    initial = {}
    if not obj and request.GET.get('colaborador', '').isdigit():
        initial['colaborador'] = request.GET['colaborador']
    form = c['form'](request.POST or None, instance=obj, initial=initial)
    if request.method == 'POST' and form.is_valid():
        nuevo = form.save(commit=False)
        for campo in ('registrada_por', 'creado_por'):
            if hasattr(nuevo, campo) and not getattr(nuevo, f'{campo}_id'):
                setattr(nuevo, campo, request.user)
        nuevo.save()
        form.save_m2m()
        registrar_bitacora(request.user, 'Editó' if obj else 'Registró', c['modulo'], str(nuevo))
        messages.success(request, f'{c["singular"].capitalize()} guardada correctamente.')
        return redirect('registro_lista', clave=clave)
    return render(request, 'portal/admin/form.html', {
        'seccion': clave, 'form': form, 'c': c, 'clave': clave, 'obj': obj})


@solo_admin
@require_POST
def registro_eliminar(request, clave, pk):
    c = _config(clave)
    obj = get_object_or_404(c['modelo'], pk=pk)
    registrar_bitacora(request.user, 'Eliminó', c['modulo'], str(obj))
    obj.delete()
    messages.success(request, 'Registro eliminado.')
    return redirect('registro_lista', clave=clave)


# ---------------------------------------------------------------- Bitácora
@solo_admin
def bitacora(request):
    qs = Bitacora.objects.select_related('usuario')
    modulo = request.GET.get('modulo', '')
    q = request.GET.get('q', '').strip()
    if modulo:
        qs = qs.filter(modulo=modulo)
    if q:
        qs = qs.filter(Q(usuario__first_name__icontains=q) | Q(usuario__last_name__icontains=q)
                       | Q(usuario__username__icontains=q) | Q(descripcion__icontains=q))
    pagina = Paginator(qs, 15).get_page(request.GET.get('page'))
    parametros = request.GET.copy()
    parametros.pop('page', None)
    return render(request, 'portal/admin/bitacora.html', {
        'seccion': 'bitacora', 'pagina': pagina, 'q': q, 'modulo': modulo, 'qs': parametros.urlencode(),
        'modulos': Bitacora.objects.order_by().values_list('modulo', flat=True).distinct()})
