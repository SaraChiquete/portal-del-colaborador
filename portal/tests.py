from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Bitacora, Falta, Horario, Perfil


class PortalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('cargar_datos', verbosity=0)

    def test_login_y_redireccion_por_rol(self):
        for usuario, clave, destino in [('gerente', 'Gerente2026', 'panel'), ('subgerente', 'Subgerente2026', 'panel'),
                                        ('004218', 'Cinepolis2026', 'portal_inicio')]:
            r = self.client.post(reverse('login'), {'username': usuario, 'password': clave}, follow=True)
            self.assertEqual(r.redirect_chain[-1][0], reverse(destino), usuario)
            self.client.logout()

    def test_login_incorrecto(self):
        r = self.client.post(reverse('login'), {'username': 'gerente', 'password': 'mal'})
        self.assertContains(r, 'incorrectos')

    def test_paginas_del_panel(self):
        self.client.login(username='subgerente', password='Subgerente2026')
        urls = [reverse(n) for n in ('panel', 'colaboradores', 'colaborador_nuevo', 'horarios', 'bitacora')]
        urls += [reverse('registro_lista', args=[c]) for c in ('asistencias', 'faltas', 'incidencias', 'amonestaciones', 'eventos')]
        urls += [reverse('registro_nuevo', args=[c]) for c in ('asistencias', 'faltas', 'incidencias', 'amonestaciones', 'eventos')]
        p = Perfil.objects.filter(rol='colaborador').first()
        urls += [reverse('colaborador_detalle', args=[p.pk]), reverse('colaborador_editar', args=[p.pk])]
        for u in urls:
            self.assertEqual(self.client.get(u).status_code, 200, u)

    def test_paginas_del_colaborador(self):
        self.client.login(username='004218', password='Cinepolis2026')
        for n in ('portal_inicio', 'portal_perfil', 'portal_horario', 'portal_faltas', 'portal_amonestaciones',
                  'portal_eventos', 'portal_logros'):
            self.assertEqual(self.client.get(reverse(n)).status_code, 200, n)

    def test_colaborador_no_entra_al_panel_ni_ve_datos_ajenos(self):
        self.client.login(username='004218', password='Cinepolis2026')
        r = self.client.get(reverse('panel'), follow=True)
        self.assertEqual(r.redirect_chain[-1][0], reverse('portal_inicio'))
        propias = Falta.objects.filter(colaborador__numero_colaborador='004218').count()
        self.assertEqual(len(self.client.get(reverse('portal_faltas')).context['items']), propias)
        self.assertEqual(self.client.get(reverse('horarios_pdf')).status_code, 302)

    def test_registrar_falta_y_bitacora(self):
        self.client.login(username='gerente', password='Gerente2026')
        p = Perfil.objects.get(numero_colaborador='004219')
        antes = Bitacora.objects.count()
        r = self.client.post(reverse('registro_nuevo', args=['faltas']), {
            'colaborador': p.pk, 'fecha': timezone.localdate().isoformat(), 'motivo': 'Prueba'})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Falta.objects.filter(colaborador=p, motivo='Prueba').exists())
        self.assertEqual(Bitacora.objects.count(), antes + 1)

    def test_asignar_horario_y_pdf(self):
        self.client.login(username='gerente', password='Gerente2026')
        p = Perfil.objects.get(numero_colaborador='004218')
        area = p.areas.first()
        dia = (timezone.localdate() + timezone.timedelta(days=30)).isoformat()
        r = self.client.post(f'{reverse("horarios")}?area={area.id}', {
            'colaboradores': [p.pk], 'dias': [dia], 'tipo': 'turno', 'hora_entrada': '09:00', 'hora_salida': '17:00'})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Horario.objects.filter(colaborador=p, fecha=dia, hora_entrada='09:00').exists())
        pdf = self.client.get(reverse('horarios_pdf') + f'?area={area.id}')
        self.assertEqual(pdf['Content-Type'], 'application/pdf')
        self.assertTrue(pdf.content.startswith(b'%PDF'))

    def test_calificar(self):
        self.client.login(username='gerente', password='Gerente2026')
        p = Perfil.objects.get(numero_colaborador='004225')
        self.client.post(reverse('calificar', args=[p.pk]), {'estrellas': 5, 'comentario': 'Muy bien'})
        self.assertEqual(p.calificaciones.first().estrellas, 5)

    def test_alta_de_colaborador(self):
        self.client.login(username='gerente', password='Gerente2026')
        area = Perfil.objects.get(numero_colaborador='004218').areas.first()
        r = self.client.post(reverse('colaborador_nuevo'), {
            'nombre': 'Nuevo', 'apellidos': 'Prueba Uno', 'numero_colaborador': '009999', 'areas': [area.pk], 'activo': 'on'})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(self.client.login(username='009999', password='Cinepolis2026'))
