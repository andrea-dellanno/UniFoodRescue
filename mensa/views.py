\
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db.models import Avg, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView
from .forms import (
    AllergeneForm, CatalogoFiltroForm, CategoriaForm, GestioneSegnalazioneForm, LottoForm,
    MensaForm, PrenotazioneForm, ProdottoForm, RecensioneForm, RegistrazioneStudenteForm,
    RitiroForm, SegnalazioneForm,
)
from .models import (
    Allergene, CategoriaAlimento, LottoInvenduto, Mensa, Prenotazione, ProdottoAlimentare,
    RecensioneMensa, Ruoli, Segnalazione, StatiLotto, StatiPrenotazione, StatiSegnalazione,
)
from .permissions import amministratore_required, operatore_required, profilo_required, studente_required


def home(request):
    stats = {
        'mense': Mensa.objects.filter(attiva=True).count(),
        'lotti_disponibili': LottoInvenduto.objects.prenotabili().count(),
        'porzioni_disponibili': LottoInvenduto.objects.prenotabili().aggregate(t=Sum('quantita_disponibile'))['t'] or 0,
        'porzioni_recuperate': Prenotazione.objects.filter(stato=StatiPrenotazione.RITIRATA).aggregate(t=Sum('quantita'))['t'] or 0,
    }
    return render(request, 'mensa/home.html', {'stats': stats, 'lotti': LottoInvenduto.objects.prenotabili()[:6]})


def catalogo_lotti(request):
    form = CatalogoFiltroForm(request.GET or None)
    lotti = LottoInvenduto.objects.prenotabili()
    if form.is_valid():
        cd = form.cleaned_data
        if cd.get('q'):
            q = cd['q']
            lotti = lotti.filter(Q(prodotto__nome__icontains=q) | Q(mensa__nome__icontains=q) | Q(prodotto__descrizione__icontains=q))
        if cd.get('mensa'):
            lotti = lotti.filter(mensa=cd['mensa'])
        if cd.get('categoria'):
            lotti = lotti.filter(prodotto__categoria=cd['categoria'])
        if cd.get('senza_allergene'):
            lotti = lotti.exclude(prodotto__allergeni=cd['senza_allergene'])
        if cd.get('vegetariano'):
            lotti = lotti.filter(prodotto__vegetariano=True)
        if cd.get('vegano'):
            lotti = lotti.filter(prodotto__vegano=True)
    return render(request, 'mensa/catalogo_lotti.html', {'form': form, 'lotti': lotti.distinct()})


def dettaglio_lotto(request, pk):
    lotto = get_object_or_404(LottoInvenduto.objects.select_related('mensa', 'prodotto', 'prodotto__categoria').prefetch_related('prodotto__allergeni'), pk=pk)
    return render(request, 'mensa/dettaglio_lotto.html', {'lotto': lotto})


def registrazione(request):
    form = RegistrazioneStudenteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Registrazione completata.')
        return redirect('dashboard')
    return render(request, 'registration/registrazione.html', {'form': form})


@login_required
def dashboard(request):
    if request.user.is_studente:
        return redirect('dashboard_studente')
    if request.user.is_operatore_mensa:
        return redirect('dashboard_operatore')
    if request.user.is_amministratore_app:
        return redirect('dashboard_amministratore')
    return redirect('home')


@studente_required
@profilo_required('profilo_studente')
def dashboard_studente(request):
    s = request.user.profilo_studente
    stats = {
        'attive': s.prenotazioni.filter(stato=StatiPrenotazione.ATTIVA).count(),
        'ritirate': s.prenotazioni.filter(stato=StatiPrenotazione.RITIRATA).count(),
        'segnalazioni': s.segnalazioni.count(),
    }
    prenotazioni = s.prenotazioni.select_related('lotto__prodotto', 'lotto__mensa')[:5]
    return render(request, 'mensa/studente/dashboard.html', {'stats': stats, 'prenotazioni': prenotazioni})


@studente_required
@profilo_required('profilo_studente')
def prenota_lotto(request, pk):
    lotto = get_object_or_404(LottoInvenduto.objects.prenotabili(), pk=pk)
    form = PrenotazioneForm(request.POST or None, lotto=lotto)
    if request.method == 'POST' and form.is_valid():
        try:
            Prenotazione.objects.crea(studente=request.user.profilo_studente, lotto=lotto, quantita=form.cleaned_data['quantita'])
            messages.success(request, 'Prenotazione creata.')
            return redirect('mie_prenotazioni')
        except ValidationError as e:
            form.add_error(None, e)
    return render(request, 'mensa/studente/prenota_lotto.html', {'form': form, 'lotto': lotto})


@studente_required
@profilo_required('profilo_studente')
def mie_prenotazioni(request):
    qs = request.user.profilo_studente.prenotazioni.select_related('lotto__prodotto', 'lotto__mensa')
    return render(request, 'mensa/studente/mie_prenotazioni.html', {'prenotazioni': qs})


@studente_required
@profilo_required('profilo_studente')
def annulla_prenotazione(request, pk):
    p = get_object_or_404(request.user.profilo_studente.prenotazioni.select_related('lotto'), pk=pk)
    if request.method == 'POST':
        try:
            p.annulla()
            messages.success(request, 'Prenotazione annullata.')
        except ValidationError as e:
            messages.error(request, e.messages[0])
    return redirect('mie_prenotazioni')


@studente_required
@profilo_required('profilo_studente')
def crea_recensione(request, prenotazione_id):
    p = get_object_or_404(request.user.profilo_studente.prenotazioni.select_related('lotto__mensa'), pk=prenotazione_id, stato=StatiPrenotazione.RITIRATA)
    if hasattr(p, 'recensione'):
        messages.info(request, 'Recensione già presente.')
        return redirect('mie_prenotazioni')
    form = RecensioneForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        r = form.save(commit=False)
        r.studente = request.user.profilo_studente
        r.mensa = p.lotto.mensa
        r.prenotazione = p
        try:
            r.full_clean()
            r.save()
            messages.success(request, 'Recensione salvata.')
            return redirect('mie_prenotazioni')
        except ValidationError as e:
            form.add_error(None, e)
    return render(request, 'mensa/form.html', {'form': form, 'title': 'Recensione mensa'})


@studente_required
@profilo_required('profilo_studente')
def apri_segnalazione(request, prenotazione_id):
    p = get_object_or_404(request.user.profilo_studente.prenotazioni.select_related('lotto__mensa', 'lotto__prodotto'), pk=prenotazione_id)
    form = SegnalazioneForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        s = form.save(commit=False)
        s.autore = request.user.profilo_studente
        s.prenotazione = p
        s.save()
        messages.success(request, 'Segnalazione aperta.')
        return redirect('mie_prenotazioni')
    return render(request, 'mensa/form.html', {'form': form, 'title': 'Apri segnalazione'})


@operatore_required
@profilo_required('profilo_operatore')
def dashboard_operatore(request):
    op = request.user.profilo_operatore
    stats = {
        'lotti_aperti': LottoInvenduto.objects.filter(mensa=op.mensa, stato=StatiLotto.DISPONIBILE).count(),
        'da_ritirare': Prenotazione.objects.filter(lotto__mensa=op.mensa, stato=StatiPrenotazione.ATTIVA).count(),
        'ritiri': op.ritiri_confermati.count(),
    }
    return render(request, 'mensa/operatore/dashboard.html', {'operatore': op, 'stats': stats})


@operatore_required
@profilo_required('profilo_operatore')
def crea_lotto(request):
    op = request.user.profilo_operatore
    form = LottoForm(request.POST or None, operatore=op)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Lotto pubblicato.')
        return redirect('gestisci_lotti')
    return render(request, 'mensa/form.html', {'form': form, 'title': 'Crea lotto'})


@operatore_required
@profilo_required('profilo_operatore')
def gestisci_lotti(request):
    op = request.user.profilo_operatore
    lotti = LottoInvenduto.objects.filter(mensa=op.mensa).select_related('prodotto', 'operatore__utente')
    return render(request, 'mensa/operatore/gestisci_lotti.html', {'lotti': lotti, 'operatore': op})


@operatore_required
@profilo_required('profilo_operatore')
def modifica_lotto(request, pk):
    op = request.user.profilo_operatore
    lotto = get_object_or_404(LottoInvenduto, pk=pk, mensa=op.mensa)
    form = LottoForm(request.POST or None, instance=lotto, operatore=op)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Lotto aggiornato.')
        return redirect('gestisci_lotti')
    return render(request, 'mensa/form.html', {'form': form, 'title': 'Modifica lotto'})


@operatore_required
@profilo_required('profilo_operatore')
def chiudi_lotto(request, pk):
    op = request.user.profilo_operatore
    lotto = get_object_or_404(LottoInvenduto, pk=pk, mensa=op.mensa)
    if request.method == 'POST':
        lotto.stato = StatiLotto.CHIUSO
        lotto.save(update_fields=['stato'])
        messages.success(request, 'Lotto chiuso.')
    return redirect('gestisci_lotti')


@operatore_required
@profilo_required('profilo_operatore')
def prenotazioni_da_ritirare(request):
    op = request.user.profilo_operatore
    qs = Prenotazione.objects.filter(lotto__mensa=op.mensa, stato=StatiPrenotazione.ATTIVA).select_related('studente__utente', 'lotto__prodotto', 'lotto__mensa')
    return render(request, 'mensa/operatore/prenotazioni_da_ritirare.html', {'prenotazioni': qs})


@operatore_required
@profilo_required('profilo_operatore')
def conferma_ritiro(request, prenotazione_id):
    op = request.user.profilo_operatore
    p = get_object_or_404(Prenotazione.objects.select_related('studente__utente', 'lotto__prodotto', 'lotto__mensa'), pk=prenotazione_id, lotto__mensa=op.mensa, stato=StatiPrenotazione.ATTIVA)
    form = RitiroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        r = form.save(commit=False)
        r.prenotazione = p
        r.operatore = op
        try:
            r.save()
            messages.success(request, 'Ritiro registrato.')
            return redirect('prenotazioni_da_ritirare')
        except ValidationError as e:
            form.add_error(None, e)
    return render(request, 'mensa/form.html', {'form': form, 'title': f'Conferma ritiro: {p.lotto.prodotto.nome}'})


@operatore_required
@profilo_required('profilo_operatore')
def storico_ritiri_operatore(request):
    qs = request.user.profilo_operatore.ritiri_confermati.select_related('prenotazione__studente__utente', 'prenotazione__lotto__prodotto')
    return render(request, 'mensa/operatore/storico_ritiri.html', {'ritiri': qs})


@amministratore_required
def dashboard_amministratore(request):
    stats = {
        'mense': Mensa.objects.count(),
        'prodotti': ProdottoAlimentare.objects.count(),
        'lotti': LottoInvenduto.objects.count(),
        'porzioni_prenotate': Prenotazione.objects.aggregate(t=Sum('quantita'))['t'] or 0,
        'porzioni_ritirate': Prenotazione.objects.filter(stato=StatiPrenotazione.RITIRATA).aggregate(t=Sum('quantita'))['t'] or 0,
        'segnalazioni_aperte': Segnalazione.objects.filter(stato__in=[StatiSegnalazione.APERTA, StatiSegnalazione.IN_CARICO]).count(),
        'voto_medio': RecensioneMensa.objects.aggregate(m=Avg('voto'))['m'] or 0,
    }
    recupero = Prenotazione.objects.filter(stato=StatiPrenotazione.RITIRATA).values('lotto__mensa__nome').annotate(porzioni=Sum('quantita'))
    segnalazioni = Segnalazione.objects.select_related('autore__utente', 'prenotazione__lotto__mensa')[:10]
    return render(request, 'mensa/amministrazione/dashboard.html', {'stats': stats, 'recupero': recupero, 'segnalazioni': segnalazioni})


class AdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or getattr(self.request.user, 'ruolo', None) == Ruoli.AMMINISTRATORE


class BaseList(AdminMixin, ListView):
    template_name = 'mensa/amministrazione/list.html'
    title = ''
    create_url = ''
    fields = []
    paginate_by = 25
    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c.update(title=self.title, create_url=self.create_url, fields=self.fields)
        return c


class BaseCreate(AdminMixin, CreateView):
    template_name = 'mensa/form.html'
    title = ''
    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['title'] = self.title
        return c


class BaseUpdate(BaseCreate, UpdateView):
    pass


class MensaList(BaseList):
    model = Mensa; title = 'Mense'; create_url = 'admin_mensa_create'; fields = ['nome', 'edificio', 'indirizzo', 'attiva']
class MensaCreate(BaseCreate):
    model = Mensa; form_class = MensaForm; success_url = reverse_lazy('admin_mensa_list'); title = 'Nuova mensa'
class MensaUpdate(BaseUpdate):
    model = Mensa; form_class = MensaForm; success_url = reverse_lazy('admin_mensa_list'); title = 'Modifica mensa'

class CategoriaList(BaseList):
    model = CategoriaAlimento; title = 'Categorie'; create_url = 'admin_categoria_create'; fields = ['nome', 'descrizione']
class CategoriaCreate(BaseCreate):
    model = CategoriaAlimento; form_class = CategoriaForm; success_url = reverse_lazy('admin_categoria_list'); title = 'Nuova categoria'
class CategoriaUpdate(BaseUpdate):
    model = CategoriaAlimento; form_class = CategoriaForm; success_url = reverse_lazy('admin_categoria_list'); title = 'Modifica categoria'

class AllergeneList(BaseList):
    model = Allergene; title = 'Allergeni'; create_url = 'admin_allergene_create'; fields = ['nome', 'descrizione']
class AllergeneCreate(BaseCreate):
    model = Allergene; form_class = AllergeneForm; success_url = reverse_lazy('admin_allergene_list'); title = 'Nuovo allergene'
class AllergeneUpdate(BaseUpdate):
    model = Allergene; form_class = AllergeneForm; success_url = reverse_lazy('admin_allergene_list'); title = 'Modifica allergene'

class ProdottoList(BaseList):
    model = ProdottoAlimentare; title = 'Prodotti'; create_url = 'admin_prodotto_create'; fields = ['nome', 'categoria', 'vegetariano', 'vegano', 'attivo']
    def get_queryset(self): return super().get_queryset().select_related('categoria')
class ProdottoCreate(BaseCreate):
    model = ProdottoAlimentare; form_class = ProdottoForm; success_url = reverse_lazy('admin_prodotto_list'); title = 'Nuovo prodotto'
class ProdottoUpdate(BaseUpdate):
    model = ProdottoAlimentare; form_class = ProdottoForm; success_url = reverse_lazy('admin_prodotto_list'); title = 'Modifica prodotto'


@amministratore_required
def gestione_segnalazioni(request):
    qs = Segnalazione.objects.select_related('autore__utente', 'prenotazione__lotto__mensa', 'amministratore__utente')
    return render(request, 'mensa/amministrazione/segnalazioni.html', {'segnalazioni': qs})


@amministratore_required
def gestisci_segnalazione(request, pk):
    s = get_object_or_404(Segnalazione, pk=pk)
    form = GestioneSegnalazioneForm(request.POST or None, instance=s)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        if not obj.amministratore_id and hasattr(request.user, 'profilo_amministratore'):
            obj.amministratore = request.user.profilo_amministratore
        try:
            obj.full_clean()
            obj.save()
            messages.success(request, 'Segnalazione aggiornata.')
            return redirect('gestione_segnalazioni')
        except ValidationError as e:
            form.add_error(None, e)
    return render(request, 'mensa/form.html', {'form': form, 'title': f'Gestisci segnalazione: {s.titolo}'})
