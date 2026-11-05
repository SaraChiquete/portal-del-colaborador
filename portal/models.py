from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Area(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.nombre


class Perfil(models.Model):
    GERENTE, SUBGERENTE, COLABORADOR = 'gerente', 'subgerente', 'colaborador'
    ROLES = [(GERENTE, 'Gerente'), (SUBGERENTE, 'Subgerente'), (COLABORADOR, 'Colaborador')]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=12, choices=ROLES, default=COLABORADOR)
    numero_colaborador = models.CharField('Número de colaborador', max_length=10, unique=True)
    telefono = models.CharField(max_length=15, blank=True)
    puesto = models.CharField(max_length=60, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    areas = models.ManyToManyField(Area, blank=True, related_name='colaboradores')

    class Meta:
        ordering = ['usuario__first_name', 'usuario__last_name']

    @property
    def es_admin(self):
        return self.rol in (self.GERENTE, self.SUBGERENTE)

    @property
    def nombre_completo(self):
        return self.usuario.get_full_name() or self.usuario.username

    @property
    def iniciales(self):
        u = self.usuario
        return ((u.first_name[:1] + u.last_name[:1]) or u.username[:2]).upper()

    @property
    def areas_texto(self):
        return ', '.join(a.nombre for a in self.areas.all()) or 'Sin área'

    def __str__(self):
        return f'{self.nombre_completo} ({self.numero_colaborador})'


class Horario(models.Model):
    TURNO, DESCANSO = 'turno', 'descanso'
    TIPOS = [(TURNO, 'Turno de trabajo'), (DESCANSO, 'Descanso')]

    colaborador = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='horarios')
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='horarios')
    fecha = models.DateField()
    tipo = models.CharField(max_length=10, choices=TIPOS, default=TURNO)
    hora_entrada = models.TimeField(null=True, blank=True)
    hora_salida = models.TimeField(null=True, blank=True)
    asignado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name='+')

    class Meta:
        ordering = ['fecha', 'hora_entrada']
        constraints = [models.UniqueConstraint(fields=['colaborador', 'fecha'], name='horario_unico_por_dia')]

    @property
    def rango(self):
        if self.tipo == self.DESCANSO or not self.hora_entrada:
            return 'Descanso'
        return f'{self.hora_entrada:%H:%M}-{self.hora_salida:%H:%M}'

    def __str__(self):
        return f'{self.colaborador.nombre_completo} · {self.fecha:%d/%m/%Y} · {self.rango}'


class Asistencia(models.Model):
    ASISTENCIA, RETARDO = 'asistencia', 'retardo'
    ESTADOS = [(ASISTENCIA, 'Asistencia'), (RETARDO, 'Retardo')]

    colaborador = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default=ASISTENCIA)
    observaciones = models.CharField(max_length=200, blank=True)
    registrada_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='+')

    class Meta:
        ordering = ['-fecha']
        constraints = [models.UniqueConstraint(fields=['colaborador', 'fecha'], name='asistencia_unica_por_dia')]

    def __str__(self):
        return f'Asistencia de {self.colaborador.nombre_completo} · {self.fecha:%d/%m/%Y}'


class Falta(models.Model):
    colaborador = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='faltas')
    fecha = models.DateField()
    motivo = models.CharField(max_length=200)
    justificada = models.BooleanField(default=False)
    registrada_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='+')

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'Falta de {self.colaborador.nombre_completo} · {self.fecha:%d/%m/%Y}'


class Incidencia(models.Model):
    PENDIENTE, SEGUIMIENTO, RESUELTA = 'pendiente', 'seguimiento', 'resuelta'
    ESTADOS = [(PENDIENTE, 'Pendiente'), (SEGUIMIENTO, 'En seguimiento'), (RESUELTA, 'Resuelta')]
    TIPOS = [('omision', 'Omisión de registro'), ('cambio_turno', 'Cambio de turno'),
             ('aclaracion', 'Aclaración de registro'), ('salida_anticipada', 'Salida anticipada'),
             ('otro', 'Otro')]

    colaborador = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='incidencias')
    fecha = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPOS)
    descripcion = models.TextField()
    estado = models.CharField(max_length=12, choices=ESTADOS, default=PENDIENTE)
    registrada_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='+')

    class Meta:
        ordering = ['-fecha', '-id']

    def __str__(self):
        return f'Incidencia de {self.colaborador.nombre_completo} · {self.fecha:%d/%m/%Y}'


class Amonestacion(models.Model):
    colaborador = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='amonestaciones')
    fecha = models.DateField()
    motivo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    registrada_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='+')

    class Meta:
        ordering = ['-fecha', '-id']
        verbose_name_plural = 'amonestaciones'

    def __str__(self):
        return f'Amonestación de {self.colaborador.nombre_completo} · {self.fecha:%d/%m/%Y}'


class Calificacion(models.Model):
    colaborador = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='calificaciones')
    estrellas = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.CharField(max_length=200, blank=True)
    fecha = models.DateField()
    calificada_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='+')

    class Meta:
        ordering = ['-fecha', '-id']
        verbose_name_plural = 'calificaciones'

    def __str__(self):
        return f'{self.colaborador.nombre_completo}: {self.estrellas}★'


class Evento(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    fecha = models.DateField()
    hora = models.TimeField(null=True, blank=True)
    lugar = models.CharField(max_length=100, blank=True)
    area = models.ForeignKey(Area, null=True, blank=True, on_delete=models.SET_NULL,
                             help_text='Déjalo vacío si el evento es para todo el personal.')
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='+')

    class Meta:
        ordering = ['fecha', 'hora']

    def __str__(self):
        return self.titulo


class Bitacora(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    accion = models.CharField(max_length=20)
    modulo = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=255)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_hora', '-id']
        verbose_name_plural = 'bitácora'

    def __str__(self):
        return f'{self.fecha_hora:%d/%m/%Y %H:%M} · {self.accion} · {self.modulo}'
