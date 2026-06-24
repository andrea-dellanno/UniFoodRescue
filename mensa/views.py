from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db.models import Avg, Count, Q, Sum
from django.db.models.deletion import ProtectedError
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from .forms import (
    AllergeneForm, CategoriaForm, GestioneSegnalazioneForm, LottoForm,
    MensaForm, PrenotazioneForm, ProdottoForm, RecensioneForm, RegistrazioneStudenteForm,
    RitiroForm, SegnalazioneForm,
)
from .models import (
    Allergene, CategoriaAlimento, LottoInvenduto, Mensa, Prenotazione, ProdottoAlimentare,
    RecensioneMensa, Ruoli, Segnalazione, StatiLotto, StatiPrenotazione, StatiSegnalazione, aggiorna_stati_automatici, Ritiro, EsitiRitiro
)
from .permissions import amministratore_required, operatore_required, profilo_required, studente_required


def home(request):
    aggiorna_stati_automatici()

    if request.user.is_authenticated and request.user.is_operatore_mensa:
        operatore = request.user.profilo_operatore

        lotti_mensa = LottoInvenduto.objects.filter(
            mensa=operatore.mensa
        ).select_related(
            'prodotto',
            'mensa',
        )

        prenotazioni_attive = Prenotazione.objects.filter(
            lotto__mensa=operatore.mensa,
            stato=StatiPrenotazione.ATTIVA,
        ).select_related(
            'studente__utente',
            'lotto__prodotto',
            'lotto__mensa',
        )

        operator_stats = {
            'lotti_disponibili': lotti_mensa.filter(
                stato=StatiLotto.DISPONIBILE
            ).count(),
            'porzioni_disponibili': lotti_mensa.filter(
                stato=StatiLotto.DISPONIBILE
            ).aggregate(t=Sum('quantita_disponibile'))['t'] or 0,
            'prenotazioni_da_confermare': prenotazioni_attive.count(),
            'ritiri_confermati': operatore.ritiri_confermati.count(),
        }

        lotti_recenti = lotti_mensa.order_by(
            '-data_pubblicazione',
            '-id',
        )[:5]

        ritiri_da_confermare = prenotazioni_attive.order_by(
            'lotto__data_scadenza',
            'lotto__ora_inizio_ritiro',
        )[:5]

        return render(
            request,
            'mensa/home.html',
            {
                'is_operator_home': True,
                'operatore': operatore,
                'operator_stats': operator_stats,
                'lotti_recenti': lotti_recenti,
                'ritiri_da_confermare': ritiri_da_confermare,
            }
        )

    lotti_prenotabili = LottoInvenduto.objects.prenotabili()

    stats = {
        'mense': Mensa.objects.filter(attiva=True).count(),
        'lotti_disponibili': lotti_prenotabili.count(),
        'porzioni_disponibili': lotti_prenotabili.aggregate(
            t=Sum('quantita_disponibile')
        )['t'] or 0,
        'porzioni_recuperate': Prenotazione.objects.filter(
            stato=StatiPrenotazione.RITIRATA
        ).aggregate(t=Sum('quantita'))['t'] or 0,
    }

    context = {
        'stats': stats,
        'lotti': lotti_prenotabili[:6],
    }

    if request.user.is_authenticated and request.user.is_studente:
        studente = request.user.profilo_studente

        prenotazioni = studente.prenotazioni.select_related(
            'lotto__prodotto',
            'lotto__mensa',
        )

        segnalazioni_aperte = studente.segnalazioni.filter(
            stato__in=[
                StatiSegnalazione.APERTA,
                StatiSegnalazione.IN_CARICO,
            ]
        ).count()

        context.update(_catalogo_lotti_context(request))
        context['is_student_home'] = True
        context['student_stats'] = {
            'attive': prenotazioni.filter(
                stato=StatiPrenotazione.ATTIVA
            ).count(),
            'ritirate': prenotazioni.filter(
                stato=StatiPrenotazione.RITIRATA
            ).count(),
            'recensioni': studente.recensioni.count(),
            'segnalazioni': segnalazioni_aperte,
        }

    return render(
        request,
        'mensa/home.html',
        context,
    )


def _catalogo_lotti_context(request):
    lotti = LottoInvenduto.objects.prenotabili()

    def get_int_param(nome_parametro):
        valore = request.GET.get(nome_parametro, '')
        if valore and valore.isdigit():
            return valore
        return ''

    categoria_id = get_int_param('categoria')
    mensa_id = get_int_param('mensa')
    senza_allergene_id = get_int_param('senza_allergene')

    vegetariano = request.GET.get('vegetariano') == '1'
    vegano = request.GET.get('vegano') == '1'

    if categoria_id:
        lotti = lotti.filter(prodotto__categoria_id=categoria_id)

    if mensa_id:
        lotti = lotti.filter(mensa_id=mensa_id)

    if senza_allergene_id:
        lotti = lotti.exclude(prodotto__allergeni__id=senza_allergene_id)

    if vegetariano:
        lotti = lotti.filter(prodotto__vegetariano=True)

    if vegano:
        lotti = lotti.filter(prodotto__vegano=True)

    lotti = lotti.distinct()

    def build_filter_url(**changes):
        params = request.GET.copy()

        for key, value in changes.items():
            if value in [None, '', False]:
                params.pop(key, None)
            else:
                params[key] = str(value)

        querystring = params.urlencode()

        if querystring:
            return f'{request.path}?{querystring}'

        return request.path

    categorie_nav = []
    for categoria in CategoriaAlimento.objects.order_by('nome'):
        active = str(categoria.pk) == str(categoria_id)
        categorie_nav.append({
            'obj': categoria,
            'active': active,
            'url': build_filter_url(
                categoria='' if active else categoria.pk
            ),
        })

    mense_nav = []
    for mensa in Mensa.objects.filter(attiva=True).order_by('nome'):
        active = str(mensa.pk) == str(mensa_id)
        mense_nav.append({
            'obj': mensa,
            'active': active,
            'url': build_filter_url(
                mensa='' if active else mensa.pk
            ),
        })

    allergeni_nav = []
    for allergene in Allergene.objects.order_by('nome'):
        active = str(allergene.pk) == str(senza_allergene_id)
        allergeni_nav.append({
            'obj': allergene,
            'active': active,
            'url': build_filter_url(
                senza_allergene='' if active else allergene.pk
            ),
        })

    has_filters = any([
        categoria_id,
        mensa_id,
        senza_allergene_id,
        vegetariano,
        vegano,
    ])

    return {
        'lotti': lotti,
        'numero_lotti': lotti.count(),

        'categorie_nav': categorie_nav,
        'mense_nav': mense_nav,
        'allergeni_nav': allergeni_nav,

        'categoria_id': categoria_id,
        'mensa_id': mensa_id,
        'senza_allergene_id': senza_allergene_id,
        'vegetariano': vegetariano,
        'vegano': vegano,
        'has_filters': has_filters,

        'clear_filters_url': request.path,
        'clear_categoria_url': build_filter_url(categoria=''),
        'clear_mensa_url': build_filter_url(mensa=''),
        'clear_allergene_url': build_filter_url(senza_allergene=''),

        'vegetariano_url': build_filter_url(
            vegetariano='' if vegetariano else '1'
        ),
        'vegano_url': build_filter_url(
            vegano='' if vegano else '1'
        ),
    }


def catalogo_lotti(request):
    if not request.user.is_authenticated:
        return redirect('home')

    if request.user.is_studente:
        return redirect('home')

    aggiorna_stati_automatici()

    return render(
        request,
        'mensa/catalogo_lotti.html',
        _catalogo_lotti_context(request),
    )


def dettaglio_lotto(request, pk):
    lotto = get_object_or_404(LottoInvenduto.objects.select_related('mensa', 'prodotto', 'prodotto__categoria').prefetch_related('prodotto__allergeni'), pk=pk)
    return render(request, 'mensa/dettaglio_lotto.html', {'lotto': lotto})


def registrazione(request):
    form = RegistrazioneStudenteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Registrazione completata.')
        return redirect('home')
    return render(request, 'registration/registrazione.html', {'form': form})


@login_required
def dashboard(request):
    if request.user.is_amministratore_app:
        return redirect('dashboard_amministratore')

    return redirect('home')


@studente_required
@profilo_required('profilo_studente')
def dashboard_studente(request):
    return redirect('home')

@studente_required
@profilo_required('profilo_studente')
def prenota_lotto(request, pk):
    aggiorna_stati_automatici()

    lotto = get_object_or_404(LottoInvenduto.objects.prenotabili(), pk=pk)
    form = PrenotazioneForm(request.POST or None, lotto=lotto)

    if request.method == 'POST' and form.is_valid():
        try:
            prenotazione = Prenotazione.objects.crea(
                studente=request.user.profilo_studente,
                lotto=lotto,
                quantita=form.cleaned_data['quantita'],
            )

            messages.success(
                request,
                f'Prenotazione confermata per il lotto {prenotazione.lotto.pk:04d}.'
            )

            return redirect('mie_prenotazioni')

        except ValidationError as e:
            form.add_error(None, e)

    return render(
        request,
        'mensa/studente/prenota_lotto.html',
        {
            'form': form,
            'lotto': lotto,
        }
    )

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
    p = get_object_or_404(
        request.user.profilo_studente.prenotazioni.select_related('lotto__mensa'),
        pk=prenotazione_id,
        stato=StatiPrenotazione.RITIRATA,
    )

    if hasattr(p, 'recensione'):
        messages.info(request, 'Hai già lasciato una recensione per questa prenotazione.')
        return redirect('dettaglio_mia_recensione', pk=p.recensione.pk)

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
            return redirect('dettaglio_mia_recensione', pk=r.pk)

        except ValidationError as e:
            form.add_error(None, e)

    return render(
        request,
        'mensa/form.html',
        {
            'form': form,
            'title': 'Recensisci la mensa',
        }
    )


@studente_required
@profilo_required('profilo_studente')
def mie_recensioni(request):
    recensioni = request.user.profilo_studente.recensioni.select_related(
        'mensa',
        'prenotazione__lotto__prodotto',
    )

    return render(
        request,
        'mensa/studente/mie_recensioni.html',
        {
            'recensioni': recensioni,
        }
    )


@studente_required
@profilo_required('profilo_studente')
def dettaglio_mia_recensione(request, pk):
    recensione = get_object_or_404(
        RecensioneMensa.objects.select_related(
            'mensa',
            'prenotazione__lotto__prodotto',
            'prenotazione__lotto__mensa',
        ),
        pk=pk,
        studente=request.user.profilo_studente,
    )

    return render(
        request,
        'mensa/studente/dettaglio_recensione.html',
        {
            'recensione': recensione,
        }
    )


def recensioni_mense(request):
    ordina = request.GET.get('ordina', 'rating_desc')

    ordinamenti = {
        'rating_desc': ('-voto_medio', 'nome'),
        'rating_asc': ('voto_medio', 'nome'),
        'recensioni_desc': ('-numero_recensioni', 'nome'),
        'nome_asc': ('nome',),
    }

    if ordina not in ordinamenti:
        ordina = 'rating_desc'

    mense = (
        Mensa.objects
        .filter(recensioni__isnull=False)
        .annotate(
            voto_medio=Avg('recensioni__voto'),
            numero_recensioni=Count('recensioni'),
        )
        .prefetch_related(
            'recensioni__studente__utente',
            'recensioni__prenotazione__lotto__prodotto',
        )
        .distinct()
        .order_by(*ordinamenti[ordina])
    )

    recensioni_totali = RecensioneMensa.objects.count()
    voto_medio_generale = RecensioneMensa.objects.aggregate(v=Avg('voto'))['v'] or 0

    conteggi_voti = {
        item['voto']: item['totale']
        for item in RecensioneMensa.objects.values('voto').annotate(totale=Count('id'))
    }

    distribuzione_voti = []

    for voto in range(5, 0, -1):
        conteggio = conteggi_voti.get(voto, 0)
        percentuale = round((conteggio / recensioni_totali) * 100) if recensioni_totali else 0

        distribuzione_voti.append({
            'voto': voto,
            'conteggio': conteggio,
            'percentuale': percentuale,
        })

    stats = {
        'recensioni_totali': recensioni_totali,
        'mense_con_valutazioni': mense.count(),
        'voto_medio_generale': voto_medio_generale,
    }

    return render(
        request,
        'mensa/recensioni_mense.html',
        {
            'mense': mense,
            'stats': stats,
            'ordina': ordina,
            'distribuzione_voti': distribuzione_voti,
        }
    )

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

@studente_required
@profilo_required('profilo_studente')
def mie_prenotazioni(request):
    aggiorna_stati_automatici()

    prenotazioni = request.user.profilo_studente.prenotazioni.select_related(
        'lotto__prodotto',
        'lotto__mensa',
        'recensione',
    )

    return render(
        request,
        'mensa/studente/mie_prenotazioni.html',
        {
            'prenotazioni': prenotazioni,
        }
    )


@operatore_required
@profilo_required('profilo_operatore')
def dashboard_operatore(request):
    return redirect('home')
    aggiorna_stati_automatici()

    operatore = request.user.profilo_operatore

    lotti_mensa = LottoInvenduto.objects.filter(
        mensa=operatore.mensa
    ).select_related(
        'prodotto',
        'mensa',
    )

    prenotazioni_attive = Prenotazione.objects.filter(
        lotto__mensa=operatore.mensa,
        stato=StatiPrenotazione.ATTIVA,
    ).select_related(
        'studente__utente',
        'lotto__prodotto',
    )

    stats = {
        'lotti_disponibili': lotti_mensa.filter(
            stato=StatiLotto.DISPONIBILE
        ).count(),
        'porzioni_disponibili': lotti_mensa.filter(
            stato=StatiLotto.DISPONIBILE
        ).aggregate(t=Sum('quantita_disponibile'))['t'] or 0,
        'prenotazioni_da_confermare': prenotazioni_attive.count(),
        'ritiri_confermati': operatore.ritiri_confermati.count(),
    }

    lotti_recenti = lotti_mensa.order_by(
        '-data_pubblicazione',
        '-id',
    )[:5]

    ritiri_da_confermare = prenotazioni_attive.order_by(
        'lotto__data_scadenza',
        'lotto__ora_inizio_ritiro',
    )[:5]

    return render(
        request,
        'mensa/operatore/dashboard.html',
        {
            'operatore': operatore,
            'stats': stats,
            'lotti_recenti': lotti_recenti,
            'ritiri_da_confermare': ritiri_da_confermare,
        }
    )


@operatore_required
@profilo_required('profilo_operatore')
def crea_lotto(request):
    operatore = request.user.profilo_operatore

    form = LottoForm(
        request.POST or None,
        operatore=operatore,
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Lotto pubblicato e visibile agli studenti.')
        return redirect('gestisci_lotti')

    return render(
        request,
        'mensa/form.html',
        {
            'form': form,
            'title': 'Pubblica lotto',
            'subtitle': f'Mensa: {operatore.mensa.nome}',
            'submit_label': 'Pubblica lotto',
        }
    )


@operatore_required
@profilo_required('profilo_operatore')
def gestisci_lotti(request):
    aggiorna_stati_automatici()

    operatore = request.user.profilo_operatore

    lotti = LottoInvenduto.objects.filter(
        mensa=operatore.mensa
    ).select_related(
        'prodotto',
        'operatore__utente',
    ).order_by(
        '-data_pubblicazione',
        '-id',
    )

    stats = {
        'totali': lotti.count(),
        'disponibili': lotti.filter(stato=StatiLotto.DISPONIBILE).count(),
        'esauriti': lotti.filter(stato=StatiLotto.ESAURITO).count(),
        'scaduti': lotti.filter(stato=StatiLotto.SCADUTO).count(),
    }

    return render(
        request,
        'mensa/operatore/gestisci_lotti.html',
        {
            'lotti': lotti,
            'operatore': operatore,
            'stats': stats,
        }
    )


@operatore_required
@profilo_required('profilo_operatore')
def modifica_lotto(request, pk):
    operatore = request.user.profilo_operatore

    lotto = get_object_or_404(
        LottoInvenduto,
        pk=pk,
        mensa=operatore.mensa,
    )

    form = LottoForm(
        request.POST or None,
        instance=lotto,
        operatore=operatore,
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Lotto aggiornato.')
        return redirect('gestisci_lotti')

    return render(
        request,
        'mensa/form.html',
        {
            'form': form,
            'title': 'Modifica lotto',
            'subtitle': 'Puoi correggere disponibilità, data, fascia di ritiro e note. Lo stato viene aggiornato automaticamente.',
            'submit_label': 'Salva modifiche',
        }
    )


@operatore_required
@profilo_required('profilo_operatore')
def chiudi_lotto(request, pk):
    operatore = request.user.profilo_operatore

    lotto = get_object_or_404(
        LottoInvenduto,
        pk=pk,
        mensa=operatore.mensa,
    )

    if request.method == 'POST':
        lotto.stato = StatiLotto.CHIUSO
        lotto.save(update_fields=['stato'])
        messages.success(request, 'Lotto chiuso.')

    return redirect('gestisci_lotti')


@operatore_required
@profilo_required('profilo_operatore')
def prenotazioni_da_ritirare(request):
    aggiorna_stati_automatici()

    operatore = request.user.profilo_operatore

    prenotazioni = Prenotazione.objects.filter(
        lotto__mensa=operatore.mensa,
        stato=StatiPrenotazione.ATTIVA,
    ).select_related(
        'studente__utente',
        'lotto__prodotto',
        'lotto__mensa',
    ).order_by(
        'lotto__data_scadenza',
        'lotto__ora_inizio_ritiro',
        'id',
    )

    return render(
        request,
        'mensa/operatore/prenotazioni_da_ritirare.html',
        {
            'prenotazioni': prenotazioni,
        }
    )


@operatore_required
@profilo_required('profilo_operatore')
def conferma_ritiro(request, prenotazione_id):
    aggiorna_stati_automatici()

    if request.method != 'POST':
        return redirect('prenotazioni_da_ritirare')

    operatore = request.user.profilo_operatore

    prenotazione = get_object_or_404(
        Prenotazione.objects.select_related(
            'studente__utente',
            'lotto__prodotto',
            'lotto__mensa',
        ),
        pk=prenotazione_id,
        lotto__mensa=operatore.mensa,
        stato=StatiPrenotazione.ATTIVA,
    )

    adesso = timezone.localtime()
    lotto = prenotazione.lotto

    dentro_fascia_ritiro = (
        lotto.data_scadenza == adesso.date()
        and lotto.ora_inizio_ritiro <= adesso.time() < lotto.ora_fine_ritiro
    )

    if not dentro_fascia_ritiro:
        messages.error(
            request,
            'Puoi segnare il ritiro solo durante la fascia prevista del lotto.'
        )
        return redirect('prenotazioni_da_ritirare')

    try:
        ritiro = Ritiro(
            prenotazione=prenotazione,
            operatore=operatore,
            esito=EsitiRitiro.CONSEGNATO,
        )
        ritiro.save()

        messages.success(
            request,
            f'Lotto L-{prenotazione.lotto.pk:04d} segnato come ritirato.'
        )

    except ValidationError as e:
        messages.error(request, e.message if hasattr(e, 'message') else str(e))

    return redirect('prenotazioni_da_ritirare')


@operatore_required
@profilo_required('profilo_operatore')
def storico_ritiri_operatore(request):
    operatore = request.user.profilo_operatore

    prenotazioni = Prenotazione.objects.filter(
        lotto__mensa=operatore.mensa,
        stato__in=[
            StatiPrenotazione.RITIRATA,
            StatiPrenotazione.NON_RITIRATA,
        ],
    ).select_related(
        'studente__utente',
        'lotto__prodotto',
        'lotto__mensa',
    ).order_by(
        '-lotto__data_scadenza',
        '-lotto__ora_inizio_ritiro',
        '-id',
    )

    return render(
        request,
        'mensa/operatore/storico_ritiri.html',
        {
            'prenotazioni': prenotazioni,
        }
    )

@amministratore_required
def dashboard_amministratore(request):
    aggiorna_stati_automatici()

    totale_prenotate = Prenotazione.objects.aggregate(t=Sum('quantita'))['t'] or 0
    totale_ritirate = Prenotazione.objects.filter(
        stato=StatiPrenotazione.RITIRATA
    ).aggregate(t=Sum('quantita'))['t'] or 0

    tasso_ritiro = round((totale_ritirate / totale_prenotate) * 100, 1) if totale_prenotate else 0

    stats = {
        'mense': Mensa.objects.count(),
        'lotti_disponibili': LottoInvenduto.objects.filter(stato=StatiLotto.DISPONIBILE).count(),
        'lotti_scaduti': LottoInvenduto.objects.filter(stato=StatiLotto.SCADUTO).count(),
        'porzioni_disponibili': LottoInvenduto.objects.filter(
            stato=StatiLotto.DISPONIBILE
        ).aggregate(t=Sum('quantita_disponibile'))['t'] or 0,
        'porzioni_prenotate': totale_prenotate,
        'porzioni_ritirate': totale_ritirate,
        'prenotazioni_non_ritirate': Prenotazione.objects.filter(
            stato=StatiPrenotazione.NON_RITIRATA
        ).count(),
        'segnalazioni_aperte': Segnalazione.objects.filter(
            stato__in=[StatiSegnalazione.APERTA, StatiSegnalazione.IN_CARICO]
        ).count(),
        'voto_medio': RecensioneMensa.objects.aggregate(m=Avg('voto'))['m'] or 0,
        'tasso_ritiro': tasso_ritiro,
    }

    recupero = Prenotazione.objects.filter(
        stato=StatiPrenotazione.RITIRATA
    ).values(
        'lotto__mensa__nome'
    ).annotate(
        porzioni=Sum('quantita')
    ).order_by('-porzioni')

    prodotti_piu_prenotati = Prenotazione.objects.values(
        'lotto__prodotto__nome'
    ).annotate(
        porzioni=Sum('quantita')
    ).order_by('-porzioni')[:5]

    segnalazioni = Segnalazione.objects.select_related(
        'autore__utente',
        'prenotazione__lotto__mensa',
    )[:10]

    return render(
        request,
        'mensa/amministrazione/dashboard.html',
        {
            'stats': stats,
            'recupero': recupero,
            'prodotti_piu_prenotati': prodotti_piu_prenotati,
            'segnalazioni': segnalazioni,
        }
    )


class AdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or getattr(self.request.user, 'ruolo', None) == Ruoli.AMMINISTRATORE


class BaseList(AdminMixin, ListView):
    template_name = 'mensa/amministrazione/list.html'
    title = ''
    create_url = ''
    delete_url = ''
    fields = []
    paginate_by = 25

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c.update(
            title=self.title,
            create_url=self.create_url,
            delete_url=self.delete_url,
            fields=self.fields,
        )
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

class BaseDelete(AdminMixin, DeleteView):
    template_name = 'mensa/amministrazione/confirm_delete.html'
    title = 'Elimina elemento'

    def get_success_url(self):
        return self.success_url

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        try:
            self.object.delete()
            messages.success(request, 'Elemento eliminato correttamente.')
        except ProtectedError:
            messages.error(
                request,
                'Non puoi eliminare questo elemento perché è collegato ad altri dati del sistema.'
            )

        return redirect(success_url)


class MensaList(BaseList):
    model = Mensa
    title = 'Mense'
    create_url = 'admin_mensa_create'
    delete_url = 'admin_mensa_delete'
    fields = ['nome', 'edificio', 'indirizzo', 'attiva']


class MensaCreate(BaseCreate):
    model = Mensa
    form_class = MensaForm
    success_url = reverse_lazy('admin_mensa_list')
    title = 'Nuova mensa'


class MensaUpdate(BaseUpdate):
    model = Mensa
    form_class = MensaForm
    success_url = reverse_lazy('admin_mensa_list')
    title = 'Modifica mensa'


class MensaDelete(BaseDelete):
    model = Mensa
    success_url = reverse_lazy('admin_mensa_list')
    title = 'Elimina mensa'


class CategoriaList(BaseList):
    model = CategoriaAlimento
    title = 'Categorie'
    create_url = 'admin_categoria_create'
    delete_url = 'admin_categoria_delete'
    fields = ['nome', 'descrizione']


class CategoriaCreate(BaseCreate):
    model = CategoriaAlimento
    form_class = CategoriaForm
    success_url = reverse_lazy('admin_categoria_list')
    title = 'Nuova categoria'


class CategoriaUpdate(BaseUpdate):
    model = CategoriaAlimento
    form_class = CategoriaForm
    success_url = reverse_lazy('admin_categoria_list')
    title = 'Modifica categoria'


class CategoriaDelete(BaseDelete):
    model = CategoriaAlimento
    success_url = reverse_lazy('admin_categoria_list')
    title = 'Elimina categoria'


class AllergeneList(BaseList):
    model = Allergene
    title = 'Allergeni'
    create_url = 'admin_allergene_create'
    delete_url = 'admin_allergene_delete'
    fields = ['nome']


class AllergeneCreate(BaseCreate):
    model = Allergene
    form_class = AllergeneForm
    success_url = reverse_lazy('admin_allergene_list')
    title = 'Nuovo allergene'


class AllergeneUpdate(BaseUpdate):
    model = Allergene
    form_class = AllergeneForm
    success_url = reverse_lazy('admin_allergene_list')
    title = 'Modifica allergene'


class AllergeneDelete(BaseDelete):
    model = Allergene
    success_url = reverse_lazy('admin_allergene_list')
    title = 'Elimina allergene'


class ProdottoList(BaseList):
    model = ProdottoAlimentare
    title = 'Prodotti'
    create_url = 'admin_prodotto_create'
    delete_url = 'admin_prodotto_delete'
    fields = ['nome', 'categoria', 'vegetariano', 'vegano', 'attivo']

    def get_queryset(self):
        return super().get_queryset().select_related('categoria')


class ProdottoCreate(BaseCreate):
    model = ProdottoAlimentare
    form_class = ProdottoForm
    success_url = reverse_lazy('admin_prodotto_list')
    title = 'Nuovo prodotto'


class ProdottoUpdate(BaseUpdate):
    model = ProdottoAlimentare
    form_class = ProdottoForm
    success_url = reverse_lazy('admin_prodotto_list')
    title = 'Modifica prodotto'


class ProdottoDelete(BaseDelete):
    model = ProdottoAlimentare
    success_url = reverse_lazy('admin_prodotto_list')
    title = 'Elimina prodotto'


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
