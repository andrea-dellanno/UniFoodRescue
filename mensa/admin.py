from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(Utente)
class UtenteAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Ruolo UniFood', {'fields': ('ruolo',)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('Ruolo UniFood', {'fields': ('email', 'ruolo')}),)
    list_display = ('username', 'email', 'first_name', 'last_name', 'ruolo', 'is_staff')
    list_filter = ('ruolo', 'is_staff', 'is_superuser', 'is_active')

class ProdottoAllergeneInline(admin.TabularInline):
    model = ProdottoAllergene
    extra = 1

@admin.register(Mensa)
class MensaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'edificio', 'orario_apertura', 'orario_chiusura', 'attiva')
    search_fields = ('nome', 'edificio', 'indirizzo')
    list_filter = ('attiva',)

@admin.register(Studente)
class StudenteAdmin(admin.ModelAdmin):
    list_display = ('utente', 'matricola', 'corso_studi', 'anno_corso')

@admin.register(OperatoreMensa)
class OperatoreMensaAdmin(admin.ModelAdmin):
    list_display = ('utente', 'mensa', 'codice_operatore', 'mansione')
    list_filter = ('mensa',)

@admin.register(Amministratore)
class AmministratoreAdmin(admin.ModelAdmin):
    list_display = ('utente', 'area_responsabilita')

@admin.register(CategoriaAlimento)
class CategoriaAdmin(admin.ModelAdmin):
    search_fields = ('nome',)

@admin.register(Allergene)
class AllergeneAdmin(admin.ModelAdmin):
    search_fields = ('nome',)

@admin.register(ProdottoAlimentare)
class ProdottoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'vegetariano', 'vegano', 'attivo')
    list_filter = ('categoria', 'vegetariano', 'vegano', 'attivo')
    inlines = [ProdottoAllergeneInline]

@admin.register(LottoInvenduto)
class LottoAdmin(admin.ModelAdmin):
    list_display = ('prodotto', 'mensa', 'quantita_disponibile', 'quantita_iniziale', 'data_scadenza', 'stato')
    list_filter = ('stato', 'mensa', 'prodotto__categoria')

@admin.register(Prenotazione)
class PrenotazioneAdmin(admin.ModelAdmin):
    list_display = ('studente', 'lotto', 'quantita', 'stato', 'data_prenotazione')
    list_filter = ('stato', 'lotto__mensa')

@admin.register(Ritiro)
class RitiroAdmin(admin.ModelAdmin):
    list_display = ('prenotazione', 'operatore', 'data_ora_ritiro', 'esito')

@admin.register(RecensioneMensa)
class RecensioneAdmin(admin.ModelAdmin):
    list_display = ('mensa', 'studente', 'voto', 'data_inserimento')

@admin.register(Segnalazione)
class SegnalazioneAdmin(admin.ModelAdmin):
    list_display = ('titolo', 'autore', 'stato', 'amministratore', 'data_apertura', 'data_chiusura')
    list_filter = ('stato',)
