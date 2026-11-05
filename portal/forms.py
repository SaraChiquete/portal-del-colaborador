from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

from .models import (Amonestacion, Area, Asistencia, Calificacion, Evento, Falta, Incidencia, Perfil)

FECHA = forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
HORA = forms.TimeInput(attrs={'type': 'time'}, format='%H:%M')


def _colaboradores():
    return Perfil.objects.filter(rol=Perfil.COLABORADOR, activo=True).select_related('usuario')


class BaseForm(forms.ModelForm):
    """Estilo común y lista de colaboradores activos."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'colaborador' in self.fields:
            self.fields['colaborador'].queryset = _colaboradores()
        if 'fecha' in self.fields and not self.instance.pk:
            self.fields['fecha'].initial = timezone.localdate()


class AsistenciaForm(BaseForm):
    class Meta:
        model = Asistencia
        fields = ['colaborador', 'fecha', 'hora_entrada', 'hora_salida', 'estado', 'observaciones']
        widgets = {'fecha': FECHA, 'hora_entrada': HORA, 'hora_salida': HORA}


class FaltaForm(BaseForm):
    class Meta:
        model = Falta
        fields = ['colaborador', 'fecha', 'motivo', 'justificada']
        widgets = {'fecha': FECHA}


class IncidenciaForm(BaseForm):
    class Meta:
        model = Incidencia
        fields = ['colaborador', 'fecha', 'tipo', 'descripcion', 'estado']
        widgets = {'fecha': FECHA, 'descripcion': forms.Textarea(attrs={'rows': 3})}


class AmonestacionForm(BaseForm):
    class Meta:
        model = Amonestacion
        fields = ['colaborador', 'fecha', 'motivo', 'descripcion']
        widgets = {'fecha': FECHA, 'descripcion': forms.Textarea(attrs={'rows': 3})}


class EventoForm(BaseForm):
    class Meta:
        model = Evento
        fields = ['titulo', 'descripcion', 'fecha', 'hora', 'lugar', 'area']
        widgets = {'fecha': FECHA, 'hora': HORA, 'descripcion': forms.Textarea(attrs={'rows': 3})}


class CalificacionForm(forms.ModelForm):
    estrellas = forms.TypedChoiceField(choices=[(i, str(i)) for i in range(5, 0, -1)], coerce=int,
                                       widget=forms.RadioSelect)

    class Meta:
        model = Calificacion
        fields = ['estrellas', 'comentario']


class ColaboradorForm(forms.Form):
    nombre = forms.CharField(max_length=60)
    apellidos = forms.CharField(max_length=80)
    correo = forms.EmailField(required=False)
    numero_colaborador = forms.CharField(label='Número de colaborador (usuario de acceso)', max_length=10)
    telefono = forms.CharField(max_length=15, required=False)
    puesto = forms.CharField(max_length=60, required=False)
    fecha_ingreso = forms.DateField(required=False, widget=FECHA)
    areas = forms.ModelMultipleChoiceField(queryset=Area.objects.all(), widget=forms.CheckboxSelectMultiple,
                                           label='Áreas asignadas')
    activo = forms.BooleanField(required=False, initial=True)
    contrasena = forms.CharField(required=False, widget=forms.PasswordInput, label='Contraseña',
                                 help_text='En un alta nueva, si la dejas vacía se usa "Cinepolis2026". '
                                           'En una edición, vacía conserva la actual.')

    def __init__(self, *args, perfil=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.perfil = perfil
        if perfil and not self.is_bound:
            u = perfil.usuario
            self.initial = {
                'nombre': u.first_name, 'apellidos': u.last_name, 'correo': u.email,
                'numero_colaborador': perfil.numero_colaborador, 'telefono': perfil.telefono,
                'puesto': perfil.puesto, 'fecha_ingreso': perfil.fecha_ingreso,
                'areas': perfil.areas.all(), 'activo': perfil.activo,
            }

    def clean_numero_colaborador(self):
        numero = self.cleaned_data['numero_colaborador'].strip()
        existentes = User.objects.filter(username=numero)
        if self.perfil:
            existentes = existentes.exclude(pk=self.perfil.usuario_id)
        if existentes.exists():
            raise forms.ValidationError('Ya existe un usuario con ese número.')
        return numero

    def guardar(self):
        d = self.cleaned_data
        if self.perfil:
            perfil, usuario = self.perfil, self.perfil.usuario
        else:
            usuario, perfil = User(), Perfil(rol=Perfil.COLABORADOR)
        usuario.username = d['numero_colaborador']
        usuario.first_name, usuario.last_name, usuario.email = d['nombre'], d['apellidos'], d['correo']
        usuario.is_active = d['activo']
        if d['contrasena']:
            usuario.set_password(d['contrasena'])
        elif not usuario.pk:
            usuario.set_password('Cinepolis2026')
        usuario.save()
        perfil.usuario = usuario
        perfil.numero_colaborador = d['numero_colaborador']
        perfil.telefono, perfil.puesto = d['telefono'], d['puesto']
        perfil.fecha_ingreso, perfil.activo = d['fecha_ingreso'], d['activo']
        perfil.save()
        perfil.areas.set(d['areas'])
        return perfil
