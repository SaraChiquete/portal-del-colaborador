from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views_admin as a
from . import views_portal as c

urlpatterns = [
    path('', c.inicio, name='inicio'),
    path('login/', LoginView.as_view(template_name='portal/login.html', redirect_authenticated_user=True),
         name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Panel de administración (gerente y subgerente)
    path('panel/', a.dashboard, name='panel'),
    path('panel/colaboradores/', a.colaboradores, name='colaboradores'),
    path('panel/colaboradores/nuevo/', a.colaborador_form, name='colaborador_nuevo'),
    path('panel/colaboradores/<int:pk>/', a.colaborador_detalle, name='colaborador_detalle'),
    path('panel/colaboradores/<int:pk>/editar/', a.colaborador_form, name='colaborador_editar'),
    path('panel/colaboradores/<int:pk>/calificar/', a.calificar, name='calificar'),
    path('panel/horarios/', a.horarios, name='horarios'),
    path('panel/horarios/pdf/', a.horarios_pdf, name='horarios_pdf'),
    path('panel/horarios/<int:pk>/eliminar/', a.horario_eliminar, name='horario_eliminar'),
    path('panel/bitacora/', a.bitacora, name='bitacora'),
    path('panel/<slug:clave>/', a.registro_lista, name='registro_lista'),
    path('panel/<slug:clave>/nuevo/', a.registro_form, name='registro_nuevo'),
    path('panel/<slug:clave>/<int:pk>/editar/', a.registro_form, name='registro_editar'),
    path('panel/<slug:clave>/<int:pk>/eliminar/', a.registro_eliminar, name='registro_eliminar'),

    # Portal del colaborador
    path('mi/', c.portal_inicio, name='portal_inicio'),
    path('mi/perfil/', c.portal_perfil, name='portal_perfil'),
    path('mi/horario/', c.portal_horario, name='portal_horario'),
    path('mi/faltas/', c.portal_faltas, name='portal_faltas'),
    path('mi/amonestaciones/', c.portal_amonestaciones, name='portal_amonestaciones'),
    path('mi/eventos/', c.portal_eventos, name='portal_eventos'),
    path('mi/logros/', c.portal_logros, name='portal_logros'),
]
