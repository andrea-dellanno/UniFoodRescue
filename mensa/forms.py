from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum
from .models import (
    Allergene, CategoriaAlimento, LottoInvenduto, Mensa, Prenotazione, ProdottoAlimentare,
    RecensioneMensa, Ritiro, Ruoli, Segnalazione, StatiSegnalazione, StatiPrenotazione, Studente, StatiLotto,Utente,
)
BOOTSTRAP = 'form-control'

class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            if isinstance(f.widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                f.widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(f.widget, (forms.Select, forms.SelectMultiple)):
                f.widget.attrs.setdefault('class', 'form-select')
            else:
                f.widget.attrs.setdefault('class', BOOTSTRAP)


class RegistrazioneStudenteForm(UserCreationForm):
    first_name = forms.CharField(
        label='Nome',
        max_length=150,
        error_messages={'required': 'Campo obbligatorio.'},
        widget=forms.TextInput(attrs={
            'placeholder': 'Nome',
            'autocomplete': 'given-name',
        })
    )

    last_name = forms.CharField(
        label='Cognome',
        max_length=150,
        error_messages={'required': 'Campo obbligatorio.'},
        widget=forms.TextInput(attrs={
            'placeholder': 'Cognome',
            'autocomplete': 'family-name',
        })
    )

    email = forms.EmailField(
        label='Email',
        error_messages={'required': 'Campo obbligatorio.'},
        widget=forms.EmailInput(attrs={
            'placeholder': 'nome@universita.it',
            'autocomplete': 'email',
        })
    )

    matricola = forms.CharField(
        label='Matricola',
        max_length=20,
        error_messages={'required': 'Campo obbligatorio.'},
        widget=forms.TextInput(attrs={
            'placeholder': 'Numero di matricola',
            'autocomplete': 'off',
        })
    )

    corso_studi = forms.CharField(
        label='Corso di studi',
        max_length=120,
        error_messages={'required': 'Campo obbligatorio.'},
        widget=forms.TextInput(attrs={
            'placeholder': 'Es. Informatica',
            'autocomplete': 'organization-title',
        })
    )

    anno_corso = forms.IntegerField(
        label='Anno di corso',
        min_value=1,
        max_value=6,
        error_messages={'required': 'Campo obbligatorio.'},
        widget=forms.NumberInput(attrs={
            'placeholder': 'Es. 1',
            'min': 1,
            'max': 6,
        })
    )

    class Meta:
        model = Utente
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'matricola',
            'corso_studi',
            'anno_corso',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        labels = {
            'username': 'Username',
            'password1': 'Password',
            'password2': 'Conferma password',
        }

        placeholders = {
            'username': 'Scegli uno username',
            'password1': 'Inserisci una password',
            'password2': 'Inserisci di nuovo la password',
        }

        help_texts = {
            'username': '',
            'password1': 'Usa almeno 8 caratteri.',
            'password2': '',
        }

        for name, field in self.fields.items():
            if name in labels:
                field.label = labels[name]

            if name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[name]

            field.help_text = help_texts.get(name, field.help_text)
            field.error_messages['required'] = 'Campo obbligatorio.'

            field.widget.attrs.setdefault('class', BOOTSTRAP)
            field.widget.attrs.setdefault('autocomplete', 'off')

            if self.is_bound and name in self.errors:
                current_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{current_class} is-invalid'.strip()
                field.widget.attrs['aria-invalid'] = 'true'

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if Utente.objects.filter(email=email).exists():
            raise ValidationError('Email già registrata.')
        return email

    def clean_matricola(self):
        matricola = self.cleaned_data['matricola']
        if Studente.objects.filter(matricola=matricola).exists():
            raise ValidationError('Matricola già registrata.')
        return matricola

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.ruolo = Ruoli.STUDENTE

        if commit:
            user.save()
            Studente.objects.create(
                utente=user,
                matricola=self.cleaned_data['matricola'],
                corso_studi=self.cleaned_data['corso_studi'],
                anno_corso=self.cleaned_data['anno_corso'],
            )

        return user

class CatalogoFiltroForm(forms.Form):
    q = forms.CharField(required=False, label='Cerca', widget=forms.TextInput(attrs={'class': BOOTSTRAP, 'placeholder': 'Prodotto o mensa'}))
    mensa = forms.ModelChoiceField(Mensa.objects.filter(attiva=True), required=False, empty_label='Tutte le mense', widget=forms.Select(attrs={'class': 'form-select'}))
    categoria = forms.ModelChoiceField(CategoriaAlimento.objects.all(), required=False, empty_label='Tutte le categorie', widget=forms.Select(attrs={'class': 'form-select'}))
    senza_allergene = forms.ModelChoiceField(Allergene.objects.all(), required=False, empty_label='Escludi allergene', widget=forms.Select(attrs={'class': 'form-select'}))
    vegetariano = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    vegano = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))


class LottoForm(BootstrapModelForm):
    class Meta:
        model = LottoInvenduto
        fields = [
            'prodotto',
            'quantita_disponibile',
            'data_scadenza',
            'ora_inizio_ritiro',
            'ora_fine_ritiro',
            'prezzo_simbolico',
            'note',
        ]
        labels = {
            'prodotto': 'Prodotto',
            'quantita_disponibile': 'Porzioni disponibili',
            'data_scadenza': 'Data ritiro',
            'ora_inizio_ritiro': 'Ora inizio ritiro',
            'ora_fine_ritiro': 'Ora fine ritiro',
            'prezzo_simbolico': 'Prezzo simbolico',
            'note': 'Note per gli studenti',
        }
        help_texts = {
            'quantita_disponibile': 'Alla pubblicazione coincide con la quantità iniziale. Dopo le prenotazioni si aggiorna automaticamente.',
            'note': 'Facoltativo: indica dettagli utili sul ritiro o sul contenuto del lotto.',
        }
        widgets = {
            'data_scadenza': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'},
            ),
            'ora_inizio_ritiro': forms.TimeInput(
                format='%H:%M',
                attrs={'type': 'time'},
            ),
            'ora_fine_ritiro': forms.TimeInput(
                format='%H:%M',
                attrs={'type': 'time'},
            ),
            'prezzo_simbolico': forms.NumberInput(
                attrs={
                    'min': '0',
                    'step': '0.01',
                    'placeholder': 'Es. 0.00',
                }
            ),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, operatore=None, **kwargs):
        self.operatore = operatore
        super().__init__(*args, **kwargs)

        self.quantita_prenotata = 0

        if self.instance and self.instance.pk:
            self.quantita_prenotata = self.instance.prenotazioni.exclude(
                stato=StatiPrenotazione.ANNULLATA
            ).aggregate(
                totale=Sum('quantita')
            )['totale'] or 0

            disponibilita_calcolata = max(
                self.instance.quantita_iniziale - self.quantita_prenotata,
                0,
            )

            self.instance.quantita_disponibile = disponibilita_calcolata
            self.initial['quantita_disponibile'] = disponibilita_calcolata

            if self.quantita_prenotata > 0:
                self.fields['quantita_disponibile'].disabled = True
                self.fields['quantita_disponibile'].help_text = (
                    f'Non modificabile: {self.quantita_prenotata} porzioni sono già collegate a prenotazioni. '
                    'La disponibilità viene calcolata automaticamente.'
                )

        self.fields['prodotto'].queryset = ProdottoAlimentare.objects.filter(
            attivo=True
        ).select_related('categoria')

        self.fields['quantita_disponibile'].widget.attrs.update({
            'min': 0,
            'placeholder': 'Es. 8',
        })

        self.fields['data_scadenza'].input_formats = ['%Y-%m-%d']
        self.fields['ora_inizio_ritiro'].input_formats = ['%H:%M']
        self.fields['ora_fine_ritiro'].input_formats = ['%H:%M']

    def clean(self):
        cleaned_data = super().clean()

        data_ritiro = cleaned_data.get('data_scadenza')
        ora_fine = cleaned_data.get('ora_fine_ritiro')

        if not self.instance.pk and data_ritiro and ora_fine:
            adesso = timezone.localtime()

            if data_ritiro < adesso.date() or (
                data_ritiro == adesso.date() and ora_fine <= adesso.time()
            ):
                raise ValidationError(
                    'La finestra di ritiro deve essere futura per pubblicare un nuovo lotto.'
                )

        return cleaned_data

    def save(self, commit=True):
        lotto = super().save(commit=False)

        if self.operatore:
            lotto.operatore = self.operatore
            lotto.mensa = self.operatore.mensa

        if lotto.pk is None:
            lotto.quantita_iniziale = lotto.quantita_disponibile

        else:
            if self.quantita_prenotata > 0:
                lotto.quantita_disponibile = max(
                    lotto.quantita_iniziale - self.quantita_prenotata,
                    0,
                )
            else:
                lotto.quantita_iniziale = lotto.quantita_disponibile

        adesso = timezone.localtime()

        finestra_passata = (
            lotto.data_scadenza < adesso.date()
            or (
                lotto.data_scadenza == adesso.date()
                and lotto.ora_fine_ritiro <= adesso.time()
            )
        )

        if lotto.stato != StatiLotto.CHIUSO:
            if finestra_passata:
                lotto.stato = StatiLotto.SCADUTO
            elif lotto.quantita_disponibile == 0:
                lotto.stato = StatiLotto.ESAURITO
            else:
                lotto.stato = StatiLotto.DISPONIBILE

        if commit:
            lotto.full_clean()
            lotto.save()

        return lotto


class PrenotazioneForm(forms.Form):
    quantita = forms.IntegerField(
        label='Quantità',
        min_value=1,
        max_value=99,
        widget=forms.NumberInput(
            attrs={
                'min': 1,
                'max': 99,
                'placeholder': 'Es. 1',
            }
        ),
    )

    def __init__(self, *args, lotto=None, **kwargs):
        self.lotto = lotto
        super().__init__(*args, **kwargs)

        massimo_prenotabile = 99

        if self.lotto:
            massimo_prenotabile = min(99, self.lotto.quantita_disponibile)

        self.fields['quantita'].widget.attrs.update({
            'max': massimo_prenotabile,
        })

    def clean_quantita(self):
        quantita = self.cleaned_data['quantita']

        if quantita > 99:
            raise ValidationError(
                'Puoi prenotare al massimo 99 porzioni per volta.'
            )

        if self.lotto and quantita > self.lotto.quantita_disponibile:
            raise ValidationError(
                'La quantità richiesta supera le porzioni disponibili.'
            )

        return quantita


class RitiroForm(BootstrapModelForm):
    class Meta:
        model = Ritiro
        fields = ['esito', 'note']
        widgets = {'note': forms.Textarea(attrs={'rows': 3})}


class RecensioneForm(BootstrapModelForm):
    voto = forms.TypedChoiceField(
        label='Valutazione',
        required=True,
        coerce=int,
        choices=[
            ('', 'Seleziona una valutazione'),
            (1, '1 - Molto negativa'),
            (2, '2 - Negativa'),
            (3, '3 - Sufficiente'),
            (4, '4 - Positiva'),
            (5, '5 - Ottima'),
        ],
        widget=forms.Select(),
        error_messages={
            'required': 'Seleziona una valutazione da 1 a 5.',
            'invalid_choice': 'La valutazione deve essere compresa tra 1 e 5.',
        },
    )

    class Meta:
        model = RecensioneMensa
        fields = [
            'voto',
            'commento',
        ]
        labels = {
            'commento': 'Commento',
        }
        help_texts = {
            'voto': 'La valutazione è obbligatoria.',
        }
        widgets = {
            'commento': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Opzionale: racconta com’è andata la tua esperienza in mensa.',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['commento'].required = False
        self.fields['commento'].label = 'Commento'

    def clean_voto(self):
        voto = self.cleaned_data.get('voto')

        if voto not in [1, 2, 3, 4, 5]:
            raise ValidationError(
                'La valutazione deve essere compresa tra 1 e 5.'
            )

        return voto


class SegnalazioneForm(BootstrapModelForm):
    class Meta:
        model = Segnalazione
        fields = ['titolo', 'descrizione']
        widgets = {'descrizione': forms.Textarea(attrs={'rows': 4})}


class GestioneSegnalazioneForm(BootstrapModelForm):
    class Meta:
        model = Segnalazione
        fields = ['stato', 'esito']
        widgets = {'esito': forms.Textarea(attrs={'rows': 4})}


class MensaForm(BootstrapModelForm):
    class Meta:
        model = Mensa
        fields = ['nome', 'edificio', 'indirizzo', 'orario_apertura', 'orario_chiusura', 'attiva']
        widgets = {'orario_apertura': forms.TimeInput(attrs={'type': 'time'}), 'orario_chiusura': forms.TimeInput(attrs={'type': 'time'})}


class CategoriaForm(BootstrapModelForm):
    class Meta:
        model = CategoriaAlimento
        fields = ['nome', 'descrizione']


class AllergeneForm(BootstrapModelForm):
    class Meta:
        model = Allergene
        fields = ['nome']


class ProdottoForm(BootstrapModelForm):
    allergeni = forms.ModelMultipleChoiceField(queryset=Allergene.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = ProdottoAlimentare
        fields = ['categoria', 'nome', 'descrizione', 'vegetariano', 'vegano', 'attivo', 'allergeni']
