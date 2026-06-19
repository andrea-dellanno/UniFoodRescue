\
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import (
    Allergene, CategoriaAlimento, LottoInvenduto, Mensa, Prenotazione, ProdottoAlimentare,
    RecensioneMensa, Ritiro, Ruoli, Segnalazione, StatiSegnalazione, Studente, Utente,
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
    first_name = forms.CharField(label='Nome', max_length=150)
    last_name = forms.CharField(label='Cognome', max_length=150)
    email = forms.EmailField(label='Email')
    matricola = forms.CharField(max_length=20)
    corso_studi = forms.CharField(max_length=120)
    anno_corso = forms.IntegerField(min_value=1, max_value=6)

    class Meta:
        model = Utente
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', BOOTSTRAP)

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
        fields = ['prodotto', 'quantita_iniziale', 'quantita_disponibile', 'data_scadenza', 'ora_inizio_ritiro', 'ora_fine_ritiro', 'prezzo_simbolico', 'stato', 'note']
        widgets = {
            'data_scadenza': forms.DateInput(attrs={'type': 'date'}),
            'ora_inizio_ritiro': forms.TimeInput(attrs={'type': 'time'}),
            'ora_fine_ritiro': forms.TimeInput(attrs={'type': 'time'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, operatore=None, **kwargs):
        self.operatore = operatore
        super().__init__(*args, **kwargs)
        self.fields['prodotto'].queryset = ProdottoAlimentare.objects.filter(attivo=True).select_related('categoria')

    def save(self, commit=True):
        lotto = super().save(commit=False)
        if self.operatore:
            lotto.operatore = self.operatore
            lotto.mensa = self.operatore.mensa
        if commit:
            lotto.full_clean()
            lotto.save()
        return lotto


class PrenotazioneForm(forms.Form):
    quantita = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': BOOTSTRAP}))

    def __init__(self, *args, lotto=None, **kwargs):
        self.lotto = lotto
        super().__init__(*args, **kwargs)
        if lotto:
            self.fields['quantita'].widget.attrs['max'] = lotto.quantita_disponibile
            self.fields['quantita'].help_text = f'Disponibili: {lotto.quantita_disponibile}'

    def clean_quantita(self):
        q = self.cleaned_data['quantita']
        if self.lotto and q > self.lotto.quantita_disponibile:
            raise ValidationError('Quantità superiore alla disponibilità.')
        return q


class RitiroForm(BootstrapModelForm):
    class Meta:
        model = Ritiro
        fields = ['esito', 'note']
        widgets = {'note': forms.Textarea(attrs={'rows': 3})}


class RecensioneForm(BootstrapModelForm):
    class Meta:
        model = RecensioneMensa
        fields = ['voto', 'commento']
        widgets = {'commento': forms.Textarea(attrs={'rows': 4})}


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
        fields = ['nome', 'descrizione']


class ProdottoForm(BootstrapModelForm):
    allergeni = forms.ModelMultipleChoiceField(queryset=Allergene.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = ProdottoAlimentare
        fields = ['categoria', 'nome', 'descrizione', 'vegetariano', 'vegano', 'attivo', 'allergeni']
