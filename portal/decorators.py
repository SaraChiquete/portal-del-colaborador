from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect


def _requiere_rol(admin):
    def decorador(vista):
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            perfil = getattr(request.user, 'perfil', None)
            if perfil is None or perfil.es_admin != admin:
                return redirect('inicio')
            return vista(request, *args, **kwargs)
        return envoltura
    return decorador


solo_admin = _requiere_rol(True)          # gerente y subgerente
solo_colaborador = _requiere_rol(False)   # cinepolito
