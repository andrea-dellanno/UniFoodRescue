from datetime import time, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Amministratore,
    CategoriaAlimento,
    EsitiRitiro,
    LottoInvenduto,
    Mensa,
    OperatoreMensa,
    Prenotazione,
    ProdottoAlimentare,
    RecensioneMensa,
    Ritiro,
    Ruoli,
    StatiPrenotazione,
    Studente,
    Utente,
)


class WorkflowPrenotazioneTest(TestCase):
    def setUp(self):
        self.mensa = Mensa.objects.create(
            nome='Mensa Test',
            edificio='A',
            indirizzo='Via Test',
            orario_apertura=time(8),
            orario_chiusura=time(20),
        )
        self.categoria = CategoriaAlimento.objects.create(nome='Primo')
        self.prodotto = ProdottoAlimentare.objects.create(
            categoria=self.categoria,
            nome='Pasta',
            vegetariano=True,
        )
        u1 = Utente.objects.create_user(
            username='stud',
            password='Test1234!',
            email='stud@test.it',
            ruolo=Ruoli.STUDENTE,
        )
        self.studente = Studente.objects.create(
            utente=u1,
            matricola='S1',
            corso_studi='Informatica',
            anno_corso=1,
        )
        u2 = Utente.objects.create_user(
            username='op',
            password='Test1234!',
            email='op@test.it',
            ruolo=Ruoli.OPERATORE,
        )
        self.operatore = OperatoreMensa.objects.create(
            utente=u2,
            mensa=self.mensa,
            codice_operatore='OP1',
            mansione='Banco',
        )

        domani = timezone.localdate() + timedelta(days=1)

        self.lotto = LottoInvenduto.objects.create(
            mensa=self.mensa,
            prodotto=self.prodotto,
            operatore=self.operatore,
            quantita_iniziale=5,
            quantita_disponibile=5,
            data_scadenza=domani,
            ora_inizio_ritiro=time(17),
            ora_fine_ritiro=time(18),
        )

    def test_prenotazione_decrementa_quantita(self):
        Prenotazione.objects.crea(
            studente=self.studente,
            lotto=self.lotto,
            quantita=2,
        )
        self.lotto.refresh_from_db()
        self.assertEqual(self.lotto.quantita_disponibile, 3)

    def test_non_supera_quantita(self):
        with self.assertRaises(ValidationError):
            Prenotazione.objects.crea(
                studente=self.studente,
                lotto=self.lotto,
                quantita=99,
            )

    def test_ritiro_consegnato_rende_prenotazione_ritirata(self):
        prenotazione = Prenotazione.objects.crea(
            studente=self.studente,
            lotto=self.lotto,
            quantita=1,
        )

        Ritiro.objects.create(
            prenotazione=prenotazione,
            operatore=self.operatore,
            esito=EsitiRitiro.CONSEGNATO,
        )

        prenotazione.refresh_from_db()
        self.assertEqual(prenotazione.stato, StatiPrenotazione.RITIRATA)

    def test_ritiro_non_consegnato_rende_prenotazione_non_ritirata(self):
        prenotazione = Prenotazione.objects.crea(
            studente=self.studente,
            lotto=self.lotto,
            quantita=1,
        )

        Ritiro.objects.create(
            prenotazione=prenotazione,
            operatore=self.operatore,
            esito=EsitiRitiro.NON_CONSEGNATO,
        )

        prenotazione.refresh_from_db()
        self.assertEqual(prenotazione.stato, StatiPrenotazione.NON_RITIRATA)

    def test_recensione_permessa_solo_dopo_ritiro(self):
        prenotazione = Prenotazione.objects.crea(
            studente=self.studente,
            lotto=self.lotto,
            quantita=1,
        )

        recensione = RecensioneMensa(
            studente=self.studente,
            mensa=self.mensa,
            prenotazione=prenotazione,
            voto=5,
            commento='Ottimo servizio.',
        )

        with self.assertRaises(ValidationError):
            recensione.full_clean()

        Ritiro.objects.create(
            prenotazione=prenotazione,
            operatore=self.operatore,
            esito=EsitiRitiro.CONSEGNATO,
        )

        prenotazione.refresh_from_db()
        recensione.full_clean()


class PagineAmministrazioneTest(TestCase):
    def setUp(self):
        self.admin_user = Utente.objects.create_user(
            username='admin_test',
            password='Test1234!',
            email='admin@test.it',
            ruolo=Ruoli.AMMINISTRATORE,
        )

        Amministratore.objects.create(
            utente=self.admin_user,
            area_responsabilita='Sistema',
        )

        self.mensa = Mensa.objects.create(
            nome='Mensa Test',
            edificio='A',
            indirizzo='Via Test',
            orario_apertura=time(8),
            orario_chiusura=time(20),
        )

        self.categoria = CategoriaAlimento.objects.create(nome='Primo')

        self.prodotto = ProdottoAlimentare.objects.create(
            categoria=self.categoria,
            nome='Pasta',
            vegetariano=True,
        )

        self.client.login(
            username='admin_test',
            password='Test1234!',
        )

    def test_lista_prodotti_carica(self):
        response = self.client.get(reverse('admin_prodotto_list'))
        self.assertEqual(response.status_code, 200)

    def test_conferma_eliminazione_mensa_carica(self):
        response = self.client.get(
            reverse('admin_mensa_delete', args=[self.mensa.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_url_eliminazione_prodotto_esiste(self):
        response = self.client.get(
            reverse('admin_prodotto_delete', args=[self.prodotto.pk])
        )
        self.assertEqual(response.status_code, 200)