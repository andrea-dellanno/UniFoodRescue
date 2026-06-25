# UniFood Rescue

**UniFood Rescue** è una web application sviluppata con **Django** per supportare il recupero degli alimenti invenduti nelle mense universitarie.

L’applicazione permette agli operatori mensa di pubblicare lotti alimentari disponibili e agli studenti di consultarli, filtrarli, prenotarli e ritirarli entro una fascia oraria stabilita.

---

## Tecnologie utilizzate

Il progetto è stato realizzato con:

- Python 3
- Django
- SQLite
- HTML
- CSS
- Bootstrap
- django-axes

Il progetto utilizza **SQLite** come database locale. Non è quindi necessario installare o configurare server database esterni come MySQL o PostgreSQL.

---

## Struttura generale del progetto

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

- Python 3;
- pip;
- Git;
- un editor, ad esempio PyCharm o Visual Studio Code;
- un terminale, ad esempio PowerShell, Prompt dei comandi, terminale Linux oppure WSL.

---

## Installazione del progetto

### 1. Clonare la repository

Aprire il terminale nella cartella in cui si vuole scaricare il progetto ed eseguire:

```bash
git clone https://github.com/andrea-dellanno/UniFoodRescue.git
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

Se l’ambiente virtuale è attivo, nel terminale dovrebbe comparire:

```txt
(.venv)
```

---

### 3. Installare le dipendenze

Con l’ambiente virtuale attivo, installare le librerie richieste dal progetto:

```bash
pip install -r requirements.txt
```

---

### 4. Preparare il database

Il progetto viene consegnato con il database SQLite già popolato:

```txt
db.sqlite3
```

Il file contiene le tabelle del progetto, i dati di prova e i trigger SQL già applicati.

È comunque possibile eseguire:

```bash
python manage.py migrate
```

per verificare che tutte le migrazioni risultino applicate correttamente.
---

### 5. Creare un superutente

Se si vuole creare un nuovo account amministratore per il pannello Django Admin:

```bash
python manage.py createsuperuser
```

Durante l’esecuzione verranno richiesti username, email e password.

Se il database consegnato contiene già utenti di prova, questo passaggio può non essere necessario.

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

SQLite salva il database direttamente in un file locale del progetto, quindi non richiede l’avvio di un servizio separato.

Il database consegnato contiene già i dati necessari per provare il funzionamento dell’applicazione.

Alcuni aggiornamenti sugli stati vengono eseguiti automaticamente tramite trigger SQL.

Gli aggiornamenti che dipendono solo dal passare del tempo vengono invece gestiti dalla logica applicativa, perché i trigger SQL vengono eseguiti solo in seguito a operazioni sul database come `INSERT`, `UPDATE` o `DELETE`.

---

## Verifica del database

Per controllare che il database sia presente e leggibile, aprire la shell SQLite tramite Django:

```bash
python manage.py dbshell
```

Dentro la shell SQLite eseguire:

```sql
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
```

Dovrebbero comparire le tabelle dell’applicazione `mensa` e le tabelle interne di Django, ad esempio:

```txt
mensa_utente
mensa_mensa
mensa_lottoinvenduto
mensa_prenotazione
mensa_ritiro
mensa_recensionemensa
mensa_segnalazione
django_migrations
django_session
django_admin_log
```

Per uscire dalla shell SQLite:

```sql
.exit
```

---

## Trigger SQL

Il progetto include trigger SQL creati tramite migrazioni Django.

I trigger sono stati usati per spostare nel database alcune regole automatiche importanti. In questo modo alcune operazioni non dipendono solo dal codice Python, ma vengono controllate direttamente dal database.

I trigger principali riguardano:

- controllo dei dati di un lotto prima dell’inserimento;
- controllo dei dati di un lotto prima dell’aggiornamento;
- blocco del ritorno allo stato disponibile per lotti già scaduti;
- passaggio automatico allo stato `esaurito` quando la quantità disponibile arriva a zero;
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

Quando uno studente prenota una porzione, Django registra la prenotazione nel database.

Dopo il salvataggio, un trigger SQL aggiorna automaticamente la quantità disponibile del lotto.

Esempio:

```txt
quantità disponibile prima: 4
quantità prenotata: 1
quantità disponibile dopo: 3
```

---

## Problemi comuni

### Python non trovato

Su Windows potrebbe comparire un errore simile a:

```txt
Python non è stato trovato
```

In questo caso provare a usare:

```bash
py manage.py runserver
```

oppure verificare che l’ambiente virtuale sia attivo:

```bash
.\.venv\Scripts\activate
```

---

### Antivirus o Avast blocca SQLite

Durante l’uso di SQLite, alcuni antivirus possono mostrare un avviso relativo a `sqlite3.exe` o al file `db.sqlite3`.

Questo può accadere usando:

```bash
python manage.py dbshell
```

In questo caso è possibile consentire l’applicazione oppure aggiungere la cartella del progetto tra le eccezioni dell’antivirus.

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

Controllo tabelle:

```sql
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
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
git clone https://github.com/andrea-dellanno/UniFoodRescue.git
cd UniFoodRescue
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Aprire poi nel browser:

```txt
http://127.0.0.1:8000/
```
