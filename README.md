# UniFood Rescue

**UniFood Rescue** è una web application sviluppata con **Django** per gestire il recupero degli alimenti invenduti nelle mense universitarie.

L'obiettivo è permettere agli operatori mensa di pubblicare lotti alimentari e agli studenti di consultarli, filtrarli, prenotarli e ritirarli in una fascia oraria stabilita.

## Tecnologie utilizzate

Il progetto è stato realizzato con:

- Python 3
- Django
- SQLite
- HTML
- CSS
- Bootstrap
- django-axes

Il database utilizzato è **SQLite**, quindi non è necessario installare MySQL, PostgreSQL o altri server database esterni.

---

## Struttura generale del progetto

La struttura principale del progetto è la seguente:

```txt
UniFoodRescue/
│
├── manage.py
├── db.sqlite3
├── requirements.txt
├── README.md
│
├── unifoodrescue/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
└── mensa/
    ├── models.py
    ├── views.py
    ├── forms.py
    ├── urls.py
    ├── admin.py
    ├── migrations/
    └── templates/
```

---

## Requisiti per l’esecuzione

Per eseguire il progetto in locale servono:

- Python 3 installato;
- pip;
- Git;
- un editor, ad esempio PyCharm o Visual Studio Code;
- un terminale, ad esempio PowerShell o Prompt dei comandi.

---

## Installazione del progetto

### 1. Clonare la repository

Aprire il terminale nella cartella in cui si vuole scaricare il progetto ed eseguire:

```bash
git clone <URL_DELLA_REPOSITORY>
```

Entrare poi nella cartella del progetto:

```bash
cd UniFoodRescue
```

---

### 2. Creare l’ambiente virtuale

Su Windows:

```bash
py -m venv .venv
.\.venv\Scripts\activate
```

Su macOS, Linux o WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Quando l’ambiente virtuale è attivo, nel terminale compare:

```txt
(.venv)
```

---

### 3. Installare le dipendenze

Con l’ambiente virtuale attivo, installare le librerie necessarie:

```bash
pip install -r requirements.txt
```

---

### 4. Applicare le migrazioni

Per creare o aggiornare la struttura del database:

```bash
python manage.py migrate
```

Le migrazioni Django creano sia le tabelle dell’applicazione sia i trigger SQL utilizzati dal progetto.

---

### 5. Creare un superutente

Per accedere al pannello di amministrazione:

```bash
python manage.py createsuperuser
```

Verranno richiesti username, email e password.

---

### 6. Avviare il server

Per avviare il progetto:

```bash
python manage.py runserver
```

Il sito sarà disponibile all’indirizzo:

```txt
http://127.0.0.1:8000/
```

Il pannello admin sarà disponibile all’indirizzo:

```txt
http://127.0.0.1:8000/admin/
```

---

## Database

Il progetto utilizza il file:

```txt
db.sqlite3
```

SQLite non richiede un server separato: il database è contenuto direttamente in un file locale.

Se `db.sqlite3` è già presente nel progetto, sono disponibili anche eventuali dati di prova.  
Se il file non è presente, può essere ricreato tramite:

```bash
python manage.py migrate
```

---

## Ruoli utente

Il sistema distingue due ruoli.

### Studente

Lo studente può:

- consultare il catalogo dei lotti disponibili;
- prenotare una o più porzioni;
- visualizzare le proprie prenotazioni;
- annullare prenotazioni ancora attive;
- lasciare recensioni;
- aprire segnalazioni.

### Operatore mensa

L’operatore mensa può:

- creare nuovi lotti alimentari;
- gestire i lotti della propria mensa;
- controllare le prenotazioni ricevute;
- registrare il ritiro di una prenotazione;
- indicare l’esito del ritiro.

---

## Stati gestiti dal sistema

### Stati dei lotti

Un lotto può trovarsi in uno dei seguenti stati:

```txt
disponibile
esaurito
scaduto
chiuso
annullato
```

### Stati delle prenotazioni

Una prenotazione può trovarsi in uno dei seguenti stati:

```txt
attiva
annullata
ritirata
non_ritirata
scaduta
```

Alcuni stati vengono aggiornati automaticamente tramite trigger SQL.

Gli aggiornamenti che dipendono soltanto dal passare del tempo vengono invece gestiti dalla logica applicativa, perché i trigger SQL si attivano solo quando avviene un’operazione sul database, come `INSERT`, `UPDATE` o `DELETE`.

---

## Trigger SQL

Il progetto include trigger SQL definiti tramite migrazioni Django.

I trigger sono stati inseriti per spostare alcune regole automatiche dal codice Python al database. In questo modo il database non si limita a salvare i dati, ma controlla direttamente alcune regole di consistenza.

I trigger principali riguardano:

- validazione dei dati di un lotto prima dell’inserimento;
- validazione dei dati di un lotto prima dell’aggiornamento;
- blocco del ritorno a disponibile per lotti già scaduti;
- passaggio automatico a esaurito quando la quantità disponibile diventa zero;
- controllo della prenotazione prima dell’inserimento;
- decremento automatico della quantità disponibile dopo una prenotazione;
- blocco della modifica di lotto o quantità in una prenotazione già creata;
- restituzione automatica della quantità in caso di annullamento;
- controllo della fascia oraria per il ritiro;
- aggiornamento automatico dello stato della prenotazione dopo il ritiro.

---

## Verifica dei trigger

Per controllare i trigger presenti nel database:

```bash
python manage.py dbshell
```

Dentro la shell SQLite eseguire:

```sql
SELECT name
FROM sqlite_master
WHERE type = 'trigger'
ORDER BY name;
```

I trigger attesi sono:

```txt
trg_lotto_au_esaurito
trg_lotto_bi_valida
trg_lotto_bu_blocca_disponibile_scaduto
trg_lotto_bu_valida
trg_prenotazione_ai_decrementa_lotto
trg_prenotazione_au_annullata_restituisce_lotto
trg_prenotazione_bi_valida
trg_prenotazione_bu_controlla_modifiche
trg_ritiro_ai_aggiorna_prenotazione
trg_ritiro_bi_fascia_oraria
```

Per uscire dalla shell SQLite:

```sql
.exit
```

---

## Esempi di comportamento dei trigger

### Prenotazione di un lotto

Quando uno studente prenota una porzione, Django salva la prenotazione.  
Subito dopo, un trigger SQL decrementa la quantità disponibile del lotto.

Esempio:

```txt
quantità disponibile iniziale: 4
quantità prenotata: 1
quantità disponibile finale: 3
```

---

### Lotto esaurito

Se dopo una prenotazione la quantità disponibile arriva a zero, un trigger imposta automaticamente lo stato del lotto a:

```txt
esaurito
```

---

### Annullamento di una prenotazione

Quando una prenotazione attiva viene annullata, un trigger restituisce la quantità prenotata al lotto.

Esempio:

```txt
quantità disponibile prima dell’annullamento: 3
quantità annullata: 1
quantità disponibile dopo l’annullamento: 4
```

---

### Ritiro di una prenotazione

Quando l’operatore registra un ritiro, un trigger aggiorna automaticamente lo stato della prenotazione in base all’esito:

```txt
consegnato       → ritirata
non_consegnato   → non_ritirata
annullato        → annullata
```

---

## Note sulla progettazione

Nel modello concettuale sono state eliminate alcune ridondanze non necessarie, preferendo chiavi naturali dove possibile.

Esempi:

- l’utente può essere identificato dalla mail;
- lo studente può essere identificato dalla matricola;
- il lotto può essere identificato da un codice lotto;
- il prodotto alimentare può essere identificato dal nome;
- l’allergene può essere identificato dal nome.

Alcuni attributi sono invece mantenuti anche se in parte derivabili, perché utili all’applicazione.

Esempi:

- `quantita_disponibile`;
- `stato` del lotto;
- `stato` della prenotazione.

Questi valori rendono più semplice e veloce la consultazione del sistema e vengono mantenuti coerenti attraverso trigger SQL e logica applicativa.

---

## Problemi comuni

### Python non trovato

Se su Windows compare un errore simile a:

```txt
Python non è stato trovato
```

provare a usare:

```bash
py manage.py runserver
```

oppure verificare che l’ambiente virtuale sia attivo:

```bash
.\.venv\Scripts\activate
```

---

### Antivirus o Avast blocca SQLite

Durante l’uso di SQLite, alcuni antivirus possono mostrare un avviso relativo a `sqlite3.exe` o a `db.sqlite3`.

In quel caso è necessario consentire l’applicazione o aggiungere la cartella del progetto alle eccezioni.

Questo può succedere usando:

```bash
python manage.py dbshell
```

---

### Warning di django-axes

Se compare un warning simile a:

```txt
AXES_LOCKOUT_PARAMETERS does not contain 'ip_address'
```

non si tratta di un errore bloccante. Il progetto può comunque essere avviato.

---

## Comandi utili

Creazione ambiente virtuale:

```bash
py -m venv .venv
```

Attivazione ambiente virtuale su Windows:

```bash
.\.venv\Scripts\activate
```

Installazione dipendenze:

```bash
pip install -r requirements.txt
```

Applicazione migrazioni:

```bash
python manage.py migrate
```

Avvio server:

```bash
python manage.py runserver
```

Accesso alla shell del database:

```bash
python manage.py dbshell
```

Controllo trigger:

```sql
SELECT name
FROM sqlite_master
WHERE type = 'trigger'
ORDER BY name;
```

---

## Avvio rapido

Per avviare il progetto da zero:

```bash
git clone <URL_DELLA_REPOSITORY>
cd UniFoodRescue
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Aprire poi nel browser:

```txt
http://127.0.0.1:8000/
```
