from datetime import date, datetime, timedelta
from io import BytesIO

from django.utils import timezone

from .models import Bitacora

DIAS_CORTO = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
DIAS_LARGO = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre',
         'octubre', 'noviembre', 'diciembre']


def registrar_bitacora(usuario, accion, modulo, descripcion):
    Bitacora.objects.create(usuario=usuario, accion=accion, modulo=modulo, descripcion=descripcion[:255])


def parse_fecha(texto, defecto=None):
    try:
        return datetime.strptime(texto, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return defecto or timezone.localdate()


def lunes_de(fecha):
    return fecha - timedelta(days=fecha.weekday())


def dias_semana(lunes):
    return [lunes + timedelta(days=i) for i in range(7)]


def fecha_larga(fecha):
    return f'{DIAS_LARGO[fecha.weekday()]} {fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}'


def rango_semana(lunes):
    fin = lunes + timedelta(days=6)
    return f'{lunes.day} al {fin.day} de {MESES[fin.month - 1]} de {fin.year}'


def calcular_logros(perfil):
    """Logros del colaborador, calculados con sus propios registros (sin inventar datos)."""
    hoy = timezone.localdate()
    inicio_mes = hoy.replace(day=1)
    logros = []
    if not perfil.faltas.filter(fecha__gte=inicio_mes, justificada=False).exists():
        logros.append(('Mes sin faltas', '¡Felicidades, no tuviste faltas este mes!'))
    asist_mes = perfil.asistencias.filter(fecha__gte=inicio_mes)
    if asist_mes.exists() and not asist_mes.filter(estado='retardo').exists():
        logros.append(('Puntualidad', 'Llegaste a tiempo todos los días de este mes. ¡Sigue así!'))
    if not perfil.amonestaciones.filter(fecha__gte=hoy - timedelta(days=90)).exists():
        logros.append(('Conducta ejemplar', 'Tres meses sin amonestaciones. Gracias por tu compromiso.'))
    ultimas = list(perfil.calificaciones.values_list('estrellas', flat=True)[:3])
    if ultimas and sum(ultimas) / len(ultimas) >= 4:
        logros.append(('Desempeño estrella', 'Tu desempeño reciente ha sido sobresaliente.'))
    if perfil.fecha_ingreso and (hoy - perfil.fecha_ingreso).days >= 365:
        logros.append(('Un año en el equipo', 'Cumpliste más de un año con nosotros. ¡Gracias!'))
    return logros


def pdf_horarios(area, lunes, filas):
    """Genera el PDF del horario semanal de un área. `filas`: lista de (nombre, [Horario|None x 7])."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), leftMargin=30, rightMargin=30,
                            topMargin=30, bottomMargin=30, title=f'Horario {area.nombre}')
    estilos = getSampleStyleSheet()
    dias = dias_semana(lunes)
    encabezado = ['Colaborador'] + [f'{DIAS_CORTO[d.weekday()]} {d.day}' for d in dias]
    datos = [encabezado]
    for nombre, celdas in filas:
        datos.append([nombre] + [h.rango if h else '-' for h in celdas])
    azul = colors.HexColor('#1B2A7A')
    tabla = Table(datos, repeatRows=1, colWidths=[150] + [84] * 7)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), azul), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#C9CFE3')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F3F5FA')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    doc.build([
        Paragraph('Cinépolis Sendero Tijuana', estilos['Title']),
        Paragraph(f'Horario semanal · Área: {area.nombre} · Semana del {rango_semana(lunes)}', estilos['Heading3']),
        Spacer(1, 10), tabla, Spacer(1, 10),
        Paragraph(f'Generado el {timezone.localtime():%d/%m/%Y %H:%M}', estilos['Normal']),
    ])
    return buffer.getvalue()
