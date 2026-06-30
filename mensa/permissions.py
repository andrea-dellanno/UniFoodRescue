from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from .models import Ruoli

def role_required(*ruoli):
    def test(user):
        return user.is_authenticated and (user.is_superuser or getattr(user, 'ruolo', None) in ruoli)
    return user_passes_test(test, login_url='login')

studente_required = role_required(Ruoli.STUDENTE)
operatore_required = role_required(Ruoli.OPERATORE)
amministratore_required = role_required(Ruoli.AMMINISTRATORE)

def profilo_required(nome_relazione):
    def deco(view):
        @wraps(view)
        @login_required(login_url='login')
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, nome_relazione):
                messages.error(request, 'Profilo non configurato correttamente.')
                return redirect('home')
            return view(request, *args, **kwargs)
        return wrapper
    return deco
