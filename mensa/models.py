from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils import timezone


class Ruoli:
    STUDENTE = 'studente'
    OPERATORE = 'operatore_mensa'
    AMMINISTRATORE = 'amministratore'

    CHOICES = [
        (STUDENTE, 'Studente'),
        (OPERATORE, 'Operatore mensa'),
        (AMMINISTRATORE, 'Amministratore'),
    ]


class Utente(AbstractUser):
    email = models.EmailField(unique=True)
    ruolo = models.CharField(max_length=30, choices=Ruoli.CHOICES)

    class Meta:
        verbose_name = 'Utente'
        verbose_name_plural = 'Utenti'

    @property
    def is_studente(self):
        return self.ruolo == Ruoli.STUDENTE

    @property
    def is_operatore_mensa(self):
        return self.ruolo == Ruoli.OPERATORE

    @property
    def is_amministratore_app(self):
        return self.ruolo == Ruoli.AMMINISTRATORE or self.is_superuser

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_ruolo_display()})'


class Mensa(models.Model):
    nome = models.CharField(max_length=120, unique=True)
    edificio = models.CharField(max_length=120)
    indirizzo = models.CharField(max_length=255)
    orario_apertura = models.TimeField()
    orario_chiusura = models.TimeField()
    attiva = models.BooleanField(default=True)

    class Meta:
        ordering = ['nome']

    def clean(self):
        if (
            self.orario_apertura
            and self.orario_chiusura
            and self.orario_chiusura <= self.orario_apertura
        ):
            raise ValidationError(
                "L'orario di chiusura deve essere successivo a quello di apertura."
            )

    def __str__(self):
        return self.nome


class Studente(models.Model):
    utente = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profilo_studente',
    )
    matricola = models.CharField(max_length=20, unique=True)
    corso_studi = models.CharField(max_length=120)
    anno_corso = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    data_registrazione = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ['utente__last_name', 'utente__first_name']

    def clean(self):
        if self.utente_id and self.utente.ruolo != Ruoli.STUDENTE:
            raise ValidationError(
                'Il profilo studente richiede un utente con ruolo studente.'
            )

    def __str__(self):
        return f'{self.utente.get_full_name()} - {self.matricola}'


class OperatoreMensa(models.Model):
    utente = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profilo_operatore',
    )
    mensa = models.ForeignKey(
        Mensa,
        on_delete=models.PROTECT,
        related_name='operatori',
    )
    codice_operatore = models.CharField(max_length=30, unique=True)
    mansione = models.CharField(max_length=120)
    data_assunzione = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ['mensa__nome', 'utente__last_name']

    def clean(self):
        if self.utente_id and self.utente.ruolo != Ruoli.OPERATORE:
            raise ValidationError(
                'Il profilo operatore richiede un utente con ruolo operatore mensa.'
            )

    def __str__(self):
        return f'{self.utente.get_full_name()} - {self.mensa.nome}'


class Amministratore(models.Model):
    utente = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profilo_amministratore',
    )
    area_responsabilita = models.CharField(max_length=120)

    def clean(self):
        if self.utente_id and self.utente.ruolo != Ruoli.AMMINISTRATORE:
            raise ValidationError(
                'Il profilo amministratore richiede un utente con ruolo amministratore.'
            )

    def __str__(self):
        return f'{self.utente.get_full_name()} - {self.area_responsabilita}'


class CategoriaAlimento(models.Model):
    nome = models.CharField(max_length=80, unique=True)
    descrizione = models.TextField(blank=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Allergene(models.Model):
    nome = models.CharField(max_length=80, unique=True)
    descrizione = models.TextField(blank=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class ProdottoAlimentare(models.Model):
    categoria = models.ForeignKey(
        CategoriaAlimento,
        on_delete=models.PROTECT,
        related_name='prodotti',
    )
    nome = models.CharField(max_length=120)
    descrizione = models.TextField(blank=True)
    vegetariano = models.BooleanField(default=False)
    vegano = models.BooleanField(default=False)
    attivo = models.BooleanField(default=True)
    allergeni = models.ManyToManyField(
        Allergene,
        through='ProdottoAllergene',
        blank=True,
        related_name='prodotti',
    )

    class Meta:
        ordering = ['categoria__nome', 'nome']
        constraints = [
            models.UniqueConstraint(
                fields=['categoria', 'nome'],
                name='uniq_prodotto_per_categoria',
            )
        ]

    def clean(self):
        if self.vegano and not self.vegetariano:
            raise ValidationError(
                'Un prodotto vegano deve essere anche vegetariano.'
            )

    def __str__(self):
        return self.nome


class ProdottoAllergene(models.Model):
    prodotto = models.ForeignKey(
        ProdottoAlimentare,
        on_delete=models.CASCADE,
    )
    allergene = models.ForeignKey(
        Allergene,
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['prodotto', 'allergene'],
                name='uniq_prodotto_allergene',
            )
        ]

    def __str__(self):
        return f'{self.prodotto} - {self.allergene}'


class StatiLotto:
    DISPONIBILE = 'disponibile'
    ESAURITO = 'esaurito'
    CHIUSO = 'chiuso'
    SCADUTO = 'scaduto'
    ANNULLATO = 'annullato'

    CHOICES = [
        (DISPONIBILE, 'Disponibile'),
        (ESAURITO, 'Esaurito'),
        (CHIUSO, 'Chiuso'),
        (SCADUTO, 'Scaduto'),
        (ANNULLATO, 'Annullato'),
    ]


class LottoManager(models.Manager):
    def prenotabili(self):
        adesso = timezone.localtime()
        oggi = adesso.date()

        return (
            self.select_related(
                'mensa',
                'prodotto',
                'prodotto__categoria',
                'operatore__utente',
            )
            .prefetch_related('prodotto__allergeni')
            .filter(
                mensa__attiva=True,
                prodotto__attivo=True,
                stato=StatiLotto.DISPONIBILE,
                quantita_disponibile__gt=0,
                data_scadenza__gte=oggi,
            )
            .exclude(
                data_scadenza=oggi,
                ora_fine_ritiro__lte=adesso.time(),
            )
        )


class LottoInvenduto(models.Model):
    mensa = models.ForeignKey(
        Mensa,
        on_delete=models.PROTECT,
        related_name='lotti',
    )
    prodotto = models.ForeignKey(
        ProdottoAlimentare,
        on_delete=models.PROTECT,
        related_name='lotti',
    )
    operatore = models.ForeignKey(
        OperatoreMensa,
        on_delete=models.PROTECT,
        related_name='lotti_creati',
    )
    quantita_iniziale = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    quantita_disponibile = models.PositiveIntegerField(
        validators=[MinValueValidator(0)]
    )
    data_pubblicazione = models.DateField(default=timezone.localdate)
    data_scadenza = models.DateField()
    ora_inizio_ritiro = models.TimeField()
    ora_fine_ritiro = models.TimeField()
    prezzo_simbolico = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    stato = models.CharField(
        max_length=20,
        choices=StatiLotto.CHOICES,
        default=StatiLotto.DISPONIBILE,
    )
    note = models.TextField(blank=True)

    objects = LottoManager()

    class Meta:
        ordering = ['-data_pubblicazione', 'mensa__nome', 'ora_inizio_ritiro']

    @property
    def codice_lotto(self):
        if not self.pk:
            return 'L-0000'

        return f'L-{self.pk:04d}'

    @property
    def scaduto_temporalmente(self):
        adesso = timezone.localtime()
        oggi = adesso.date()

        if self.data_scadenza < oggi:
            return True

        if self.data_scadenza == oggi and self.ora_fine_ritiro <= adesso.time():
            return True

        return False

    @property
    def is_prenotabile(self):
        return (
            self.stato == StatiLotto.DISPONIBILE
            and self.quantita_disponibile > 0
            and not self.scaduto_temporalmente
            and self.mensa.attiva
            and self.prodotto.attivo
        )

    def clean(self):
        errors = {}

        if (
            self.quantita_disponibile is not None
            and self.quantita_iniziale is not None
            and self.quantita_disponibile > self.quantita_iniziale
        ):
            errors['quantita_disponibile'] = (
                'La quantità disponibile non può superare quella iniziale.'
            )

        if (
            self.data_pubblicazione
            and self.data_scadenza
            and self.data_scadenza < self.data_pubblicazione
        ):
            errors['data_scadenza'] = (
                'La scadenza non può precedere la pubblicazione.'
            )

        if (
            self.ora_inizio_ritiro
            and self.ora_fine_ritiro
            and self.ora_fine_ritiro <= self.ora_inizio_ritiro
        ):
            errors['ora_fine_ritiro'] = (
                'La fine ritiro deve essere successiva all’inizio.'
            )

        if (
            self.operatore_id
            and self.mensa_id
            and self.operatore.mensa_id != self.mensa_id
        ):
            errors['operatore'] = (
                'L’operatore può creare lotti solo per la propria mensa.'
            )

        if (
            self.mensa_id
            and not self.mensa.attiva
            and self.stato == StatiLotto.DISPONIBILE
        ):
            errors['mensa'] = (
                'Una mensa inattiva non può pubblicare lotti disponibili.'
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.scaduto_temporalmente and self.stato == StatiLotto.DISPONIBILE:
            self.stato = StatiLotto.SCADUTO
        elif (
            self.quantita_disponibile == 0
            and self.stato == StatiLotto.DISPONIBILE
        ):
            self.stato = StatiLotto.ESAURITO

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f'{self.codice_lotto} - {self.prodotto.nome} - '
            f'{self.mensa.nome} ({self.quantita_disponibile}/{self.quantita_iniziale})'
        )


class StatiPrenotazione:
    ATTIVA = 'attiva'
    ANNULLATA = 'annullata'
    RITIRATA = 'ritirata'
    NON_RITIRATA = 'non_ritirata'
    SCADUTA = 'scaduta'

    CHOICES = [
        (ATTIVA, 'Attiva'),
        (ANNULLATA, 'Annullata'),
        (RITIRATA, 'Ritirata'),
        (NON_RITIRATA, 'Non ritirata'),
        (SCADUTA, 'Scaduta'),
    ]


class PrenotazioneManager(models.Manager):
    def crea(self, *, studente, lotto, quantita):
        quantita = int(quantita)

        if quantita <= 0:
            raise ValidationError('La quantità deve essere maggiore di zero.')

        with transaction.atomic():
            lotto_bloccato = (
                LottoInvenduto.objects
                .select_for_update()
                .select_related('mensa', 'prodotto')
                .get(pk=lotto.pk)
            )

            if not lotto_bloccato.is_prenotabile:
                raise ValidationError('Il lotto non è prenotabile.')

            if quantita > lotto_bloccato.quantita_disponibile:
                raise ValidationError(
                    'Quantità richiesta superiore alla disponibilità.'
                )

            prenotazione = self.model(
                studente=studente,
                lotto=lotto_bloccato,
                quantita=quantita,
                stato=StatiPrenotazione.ATTIVA,
            )

            prenotazione.full_clean()

            lotto_bloccato.quantita_disponibile -= quantita

            if lotto_bloccato.quantita_disponibile == 0:
                lotto_bloccato.stato = StatiLotto.ESAURITO
            elif not lotto_bloccato.scaduto_temporalmente:
                lotto_bloccato.stato = StatiLotto.DISPONIBILE

            lotto_bloccato.save(
                update_fields=['quantita_disponibile', 'stato']
            )
            prenotazione.save()

            return prenotazione


class Prenotazione(models.Model):
    studente = models.ForeignKey(
        Studente,
        on_delete=models.PROTECT,
        related_name='prenotazioni',
    )
    lotto = models.ForeignKey(
        LottoInvenduto,
        on_delete=models.PROTECT,
        related_name='prenotazioni',
    )
    quantita = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    stato = models.CharField(
        max_length=20,
        choices=StatiPrenotazione.CHOICES,
        default=StatiPrenotazione.ATTIVA,
    )
    data_prenotazione = models.DateTimeField(default=timezone.now)

    objects = PrenotazioneManager()

    class Meta:
        ordering = ['-data_prenotazione']

    @property
    def codice_ritiro(self):
        if not self.lotto_id:
            return 'L-0000'

        return f'L-{self.lotto_id:04d}'

    @property
    def stato_interfaccia(self):
        if self.stato != StatiPrenotazione.ATTIVA:
            return self.stato

        adesso = timezone.localtime()
        oggi = adesso.date()
        ora_attuale = adesso.time()
        lotto = self.lotto

        if (
            lotto.data_scadenza > oggi
            or (
                lotto.data_scadenza == oggi
                and lotto.ora_inizio_ritiro > ora_attuale
            )
        ):
            return 'programmata'

        if (
            lotto.data_scadenza == oggi
            and lotto.ora_inizio_ritiro <= ora_attuale < lotto.ora_fine_ritiro
        ):
            return 'pronta'

        return 'scaduta_da_verificare'

    def annulla(self):
        if self.stato != StatiPrenotazione.ATTIVA:
            raise ValidationError(
                'Solo prenotazioni attive possono essere annullate.'
            )

        with transaction.atomic():
            prenotazione = (
                Prenotazione.objects
                .select_for_update()
                .select_related('lotto')
                .get(pk=self.pk)
            )

            lotto = (
                LottoInvenduto.objects
                .select_for_update()
                .get(pk=prenotazione.lotto_id)
            )

            prenotazione.stato = StatiPrenotazione.ANNULLATA
            prenotazione.save(update_fields=['stato'])

            lotto.quantita_disponibile += prenotazione.quantita

            if lotto.quantita_disponibile > lotto.quantita_iniziale:
                lotto.quantita_disponibile = lotto.quantita_iniziale

            if (
                lotto.stato == StatiLotto.ESAURITO
                and not lotto.scaduto_temporalmente
            ):
                lotto.stato = StatiLotto.DISPONIBILE

            lotto.save(update_fields=['quantita_disponibile', 'stato'])

    def __str__(self):
        return (
            f'{self.codice_ritiro} - {self.studente} - '
            f'{self.lotto.prodotto.nome} x {self.quantita}'
        )


class EsitiRitiro:
    CONSEGNATO = 'consegnato'
    NON_CONSEGNATO = 'non_consegnato'
    ANNULLATO = 'annullato'

    CHOICES = [
        (CONSEGNATO, 'Consegnato'),
        (NON_CONSEGNATO, 'Non consegnato'),
        (ANNULLATO, 'Annullato'),
    ]


class Ritiro(models.Model):
    prenotazione = models.OneToOneField(
        Prenotazione,
        on_delete=models.PROTECT,
        related_name='ritiro',
    )
    operatore = models.ForeignKey(
        OperatoreMensa,
        on_delete=models.PROTECT,
        related_name='ritiri_confermati',
    )
    data_ora_ritiro = models.DateTimeField(default=timezone.now)
    esito = models.CharField(
        max_length=20,
        choices=EsitiRitiro.CHOICES,
        default=EsitiRitiro.CONSEGNATO,
    )
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['-data_ora_ritiro']

    def clean(self):
        errors = {}

        if self.operatore_id and self.prenotazione_id:
            if self.operatore.mensa_id != self.prenotazione.lotto.mensa_id:
                errors['operatore'] = (
                    'Operatore non associato alla mensa del lotto.'
                )

            if self.prenotazione.stato != StatiPrenotazione.ATTIVA:
                errors['prenotazione'] = (
                    'Il ritiro è possibile solo per prenotazioni attive.'
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        with transaction.atomic():
            super().save(*args, **kwargs)

            prenotazione = (
                Prenotazione.objects
                .select_for_update()
                .select_related('lotto')
                .get(pk=self.prenotazione_id)
            )

            if self.esito == EsitiRitiro.CONSEGNATO:
                nuovo_stato = StatiPrenotazione.RITIRATA

            elif self.esito == EsitiRitiro.NON_CONSEGNATO:
                nuovo_stato = StatiPrenotazione.NON_RITIRATA

            else:
                nuovo_stato = StatiPrenotazione.ANNULLATA

                lotto = (
                    LottoInvenduto.objects
                    .select_for_update()
                    .get(pk=prenotazione.lotto_id)
                )

                lotto.quantita_disponibile += prenotazione.quantita

                if lotto.quantita_disponibile > lotto.quantita_iniziale:
                    lotto.quantita_disponibile = lotto.quantita_iniziale

                if (
                    lotto.stato == StatiLotto.ESAURITO
                    and not lotto.scaduto_temporalmente
                ):
                    lotto.stato = StatiLotto.DISPONIBILE

                lotto.save(update_fields=['quantita_disponibile', 'stato'])

            prenotazione.stato = nuovo_stato
            prenotazione.save(update_fields=['stato'])

    def __str__(self):
        return (
            f'Ritiro {self.prenotazione.codice_ritiro} - '
            f'{self.get_esito_display()}'
        )


class RecensioneMensa(models.Model):
    studente = models.ForeignKey(
        Studente,
        on_delete=models.PROTECT,
        related_name='recensioni',
    )
    mensa = models.ForeignKey(
        Mensa,
        on_delete=models.PROTECT,
        related_name='recensioni',
    )
    prenotazione = models.OneToOneField(
        Prenotazione,
        on_delete=models.PROTECT,
        related_name='recensione',
    )
    voto = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    commento = models.TextField(blank=True)
    data_inserimento = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-data_inserimento']

    def clean(self):
        errors = {}

        if self.prenotazione_id:
            if self.prenotazione.studente_id != self.studente_id:
                errors['studente'] = (
                    'La recensione deve appartenere allo studente della prenotazione.'
                )

            if self.prenotazione.lotto.mensa_id != self.mensa_id:
                errors['mensa'] = (
                    'La mensa recensita deve corrispondere al lotto prenotato.'
                )

            if self.prenotazione.stato != StatiPrenotazione.RITIRATA:
                errors['prenotazione'] = (
                    'Si può recensire solo dopo ritiro completato.'
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f'{self.mensa.nome} - {self.voto}/5'


class StatiSegnalazione:
    APERTA = 'aperta'
    IN_CARICO = 'in_carico'
    RISOLTA = 'risolta'
    RESPINTA = 'respinta'
    CHIUSA = 'chiusa'

    CHOICES = [
        (APERTA, 'Aperta'),
        (IN_CARICO, 'In carico'),
        (RISOLTA, 'Risolta'),
        (RESPINTA, 'Respinta'),
        (CHIUSA, 'Chiusa'),
    ]

    FINALI = {RISOLTA, RESPINTA, CHIUSA}


class Segnalazione(models.Model):
    prenotazione = models.ForeignKey(
        Prenotazione,
        on_delete=models.PROTECT,
        related_name='segnalazioni',
    )
    autore = models.ForeignKey(
        Studente,
        on_delete=models.PROTECT,
        related_name='segnalazioni',
    )
    amministratore = models.ForeignKey(
        Amministratore,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='segnalazioni_gestite',
    )
    titolo = models.CharField(max_length=160)
    descrizione = models.TextField()
    stato = models.CharField(
        max_length=20,
        choices=StatiSegnalazione.CHOICES,
        default=StatiSegnalazione.APERTA,
    )
    esito = models.TextField(blank=True)
    data_apertura = models.DateTimeField(default=timezone.now)
    data_chiusura = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['stato', '-data_apertura']

    def clean(self):
        errors = {}

        if (
            self.prenotazione_id
            and self.autore_id
            and self.prenotazione.studente_id != self.autore_id
        ):
            errors['autore'] = (
                'L’autore deve essere lo studente della prenotazione.'
            )

        if self.stato in StatiSegnalazione.FINALI and not self.esito:
            errors['esito'] = (
                'Per chiudere la segnalazione serve un esito.'
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.stato in StatiSegnalazione.FINALI and not self.data_chiusura:
            self.data_chiusura = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.titolo} - {self.get_stato_display()}'


def aggiorna_stati_automatici():
    adesso = timezone.localtime()
    oggi = adesso.date()
    ora_attuale = adesso.time()

    lotti_da_chiudere = LottoInvenduto.objects.filter(
        stato=StatiLotto.DISPONIBILE
    ).filter(
        models.Q(data_scadenza__lt=oggi)
        | models.Q(data_scadenza=oggi, ora_fine_ritiro__lte=ora_attuale)
    )

    lotti_da_chiudere_ids = list(
        lotti_da_chiudere.values_list('id', flat=True)
    )

    numero_prenotazioni_non_ritirate = Prenotazione.objects.filter(
        stato=StatiPrenotazione.ATTIVA,
        lotto_id__in=lotti_da_chiudere_ids,
    ).update(
        stato=StatiPrenotazione.NON_RITIRATA
    )

    numero_lotti_scaduti = lotti_da_chiudere.update(
        stato=StatiLotto.SCADUTO
    )

    numero_lotti_esauriti = LottoInvenduto.objects.filter(
        stato=StatiLotto.DISPONIBILE,
        quantita_disponibile=0,
    ).update(
        stato=StatiLotto.ESAURITO
    )

    return {
        'lotti_scaduti': numero_lotti_scaduti,
        'prenotazioni_non_ritirate': numero_prenotazioni_non_ritirate,
        'lotti_esauriti': numero_lotti_esauriti,
    }