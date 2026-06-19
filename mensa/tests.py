from datetime import date, time
from django.core.exceptions import ValidationError
from django.test import TestCase
from .models import *

class WorkflowPrenotazioneTest(TestCase):
    def setUp(self):
        self.mensa = Mensa.objects.create(nome='Mensa Test', edificio='A', indirizzo='Via Test', orario_apertura=time(8), orario_chiusura=time(20))
        self.categoria = CategoriaAlimento.objects.create(nome='Primo')
        self.prodotto = ProdottoAlimentare.objects.create(categoria=self.categoria, nome='Pasta', vegetariano=True)
        u1 = Utente.objects.create_user(username='stud', password='Test1234!', email='stud@test.it', ruolo=Ruoli.STUDENTE)
        self.studente = Studente.objects.create(utente=u1, matricola='S1', corso_studi='Informatica', anno_corso=1)
        u2 = Utente.objects.create_user(username='op', password='Test1234!', email='op@test.it', ruolo=Ruoli.OPERATORE)
        self.operatore = OperatoreMensa.objects.create(utente=u2, mensa=self.mensa, codice_operatore='OP1', mansione='Banco')
        self.lotto = LottoInvenduto.objects.create(mensa=self.mensa, prodotto=self.prodotto, operatore=self.operatore, quantita_iniziale=5, quantita_disponibile=5, data_scadenza=date.today(), ora_inizio_ritiro=time(17), ora_fine_ritiro=time(18))

    def test_prenotazione_decrementa_quantita(self):
        Prenotazione.objects.crea(studente=self.studente, lotto=self.lotto, quantita=2)
        self.lotto.refresh_from_db()
        self.assertEqual(self.lotto.quantita_disponibile, 3)

    def test_non_supera_quantita(self):
        with self.assertRaises(ValidationError):
            Prenotazione.objects.crea(studente=self.studente, lotto=self.lotto, quantita=99)
