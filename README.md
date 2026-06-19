# UniFood Rescue

> Sistema  Django per la gestione e il recupero delle eccedenze alimentari nelle mense universitarie.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Django](https://img.shields.io/badge/Django-darkgreen)
![Database](https://img.shields.io/badge/Database-SQL-lightgrey)


**Autore:** Andrea Dell'Anno   
**Tema:** controllo eccedenze e lotti alimentari universitari

---

## Indice

- [1. Descrizione del progetto](#1-descrizione-del-progetto)
- [2. Obiettivo del sistema](#2-obiettivo-del-sistema)
- [3. Funzionalità implementate](#3-funzionalità-implementate)
- [4. Flusso principale](#4-flusso-principale)
- [5. Generalizzazione e specializzazione](#6-generalizzazione-e-specializzazione)
- [6. Modello logico relazionale](#7-modello-logico-relazionale)
- [7. Vincoli del sistema](#8-vincoli-del-sistema)
- [8. Stati del dominio](#9-stati-del-dominio)
- [9. Scelte progettuali rilevanti](#10-scelte-progettuali-rilevanti)
- [10. Query SQL significative](#11-query-sql-significative)

---

## 1. Descrizione del progetto

**UniFood Rescue** è un'applicazione web pensata per un contesto universitario, finalizzata alla gestione e al recupero delle eccedenze alimentari prodotte dalle mense universitarie.

Il processo reale è il seguente: a fine servizio una mensa può avere prodotti alimentari ancora disponibili. Questi prodotti non devono essere trattati come pasti generici, ma come **lotti invenduti**, cioè disponibilità concrete associate a:

- una mensa precisa;
- un prodotto alimentare preciso;
- una quantità iniziale;
- una quantità ancora disponibile;
- una data di scadenza;
- una fascia oraria di ritiro;
- uno stato operativo;
- un operatore responsabile della pubblicazione.

Gli studenti possono consultare i lotti disponibili, filtrare i risultati per mensa, categoria, caratteristiche alimentari o allergeni, prenotare una quantità e ritirarla nella fascia oraria indicata. Gli operatori mensa possono invece pubblicare nuovi lotti, aggiornare le quantità, chiudere disponibilità non più valide e confermare i ritiri. Gli amministratori supervisionano il sistema,prendendo in carico le segnalazioni.

Il sistema non prevede pagamenti online, consegne a domicilio, QR code obbligatori o funzionalità mobile complesse.

La piattaforma prevede tre tipologie principali di utenti:

- **Studenti**: consultano i lotti disponibili, prenotano prodotti, visualizzano lo storico, lasciano recensioni e aprono segnalazioni.
- **Operatori mensa**: creano lotti invenduti, modificano quantità, chiudono lotti, confermano ritiri e gestiscono i prodotti della propria mensa.
- **Amministratori**: gestiscono mense, categorie, allergeni, prodotti, statistiche e segnalazioni.

---

## 2. Obiettivo del sistema

Il sistema nasce con l'obiettivo di supportare le mense universitarie nella gestione organizzata delle eccedenze alimentari giornaliere.

In molte mense, al termine del servizio, possono rimanere pasti o prodotti non distribuiti. Senza un sistema informativo strutturato, queste eccedenze rischiano di essere eliminate, gestite informalmente o distribuite senza una reale tracciabilità.

La logica principale non è quella della vendita, ma quella della **tracciabilità**. Il sistema deve rispondere a domande come:

- quale mensa ha pubblicato un certo lotto?
- quale prodotto è stato reso disponibile?
- quali allergeni contiene?
- quante porzioni erano disponibili all'inizio?
- quante sono ancora prenotabili?
- quale studente ha prenotato?
- il ritiro è stato effettivamente confermato?
- ci sono state segnalazioni o problemi?

---

## 3. Funzionalità Supportate

1. Registrazione e autenticazione degli utenti con ruolo differenziato: Studente / Operatore Mensa / Amministratore.
2. Gestione delle mense universitarie.
3. Gestione del catalogo dei prodotti alimentari.
4. Gestione delle categorie alimentari.
5. Gestione degli allergeni.
6. Associazione molti-a-molti tra prodotti alimentari e allergeni.
7. Pubblicazione di lotti invenduti da parte degli operatori mensa.
8. Visualizzazione dei lotti disponibili da parte degli studenti.
9. Ricerca e filtro dei lotti per mensa, categoria, allergene, disponibilità, vegetariano e vegano.
10. Prenotazione di una quantità di un lotto da parte dello studente.
11. Aggiornamento automatico della quantità disponibile del lotto.
12. Annullamento di una prenotazione attiva con restituzione della quantità al lotto.
13. Visualizzazione dello storico delle prenotazioni dello studente.
14. Conferma del ritiro da parte dell'operatore mensa.
15. Gestione degli stati del lotto e della prenotazione.
16. Inserimento di recensioni sulla mensa dopo un ritiro completato.
17. Apertura di segnalazioni relative a prenotazioni o ritiri problematici.
18. Presa in carico e gestione delle segnalazioni da parte dell'amministratore.
19. Dashboard riepilogativa per monitorare lotti pubblicati, porzioni prenotate, porzioni ritirate e quantità recuperate.
20. Area admin Django per la gestione completa dei dati.

---

## 4. Flusso principale

Il flusso principale dell'applicazione è il seguente:

1. Un operatore mensa accede alla piattaforma.
2. L'operatore seleziona un prodotto alimentare già registrato nel sistema.
3. L'operatore crea un lotto invenduto indicando mensa, prodotto, quantità iniziale, fascia oraria di ritiro e data di scadenza.
4. Il lotto viene pubblicato nello stato `disponibile`.
5. Uno studente accede al catalogo dei lotti disponibili.
6. Lo studente filtra i lotti in base a mensa, categoria, allergeni o caratteristiche alimentari.
7. Lo studente prenota una quantità del lotto.
8. Il sistema controlla che il lotto sia disponibile, non scaduto e con quantità sufficiente.
9. Se la prenotazione è valida, il sistema riduce la quantità disponibile del lotto.
10. Lo studente si presenta in mensa nella fascia oraria prevista.
11. L'operatore mensa conferma il ritiro.
12. La prenotazione passa allo stato `ritirata`.
13. Il sistema registra un record di ritiro.
14. Lo studente può lasciare una recensione sulla mensa.
15. In caso di problema, lo studente può aprire una segnalazione.
16. L'amministratore può prendere in carico la segnalazione e chiuderla con un esito.

In forma sintetica:

```text
OperatoreMensa -> LottoInvenduto -> Prenotazione -> Ritiro -> Recensione / Segnalazione
```

Questo flusso rappresenta il ciclo di vita completo del dato: dalla pubblicazione dell'eccedenza fino alla sua consegna effettiva o alla gestione di eventuali problemi.

---

## 5. Generalizzazione e specializzazione

Il sistema prevede una gerarchia di generalizzazione con entità padre `Utente` e tre entità figlie:

- `Studente`
- `OperatoreMensa`
- `Amministratore`

La generalizzazione è:

- **totale**, perché ogni utente registrato deve essere necessariamente uno studente, un operatore mensa o un amministratore;
- **disgiunta**, perché un utente non può appartenere contemporaneamente a più ruoli.

### Alternativa 1 — Accorpamento delle entità figlie nel padre

In questa alternativa si mantiene una sola tabella `Utente`, nella quale vengono inseriti anche gli attributi specifici di `Studente`, `OperatoreMensa` e `Amministratore`.

Schema risultante:

```text
Utente(
  id,
  username,
  password,
  nome,
  cognome,
  email,
  ruolo,
  matricola,
  corso_studi,
  anno_corso,
  data_registrazione_studente,
  codice_operatore,
  mansione,
  mensa_id,
  area_responsabilita
)
```

Vantaggi:

- una sola tabella per tutti gli utenti;
- query semplici per il recupero dei dati utente;
- nessun join necessario per ottenere il profilo completo;
- gestione centralizzata di username, email e password.

Svantaggi:

- presenza di molti valori `NULL`;
- gli attributi dello studente non hanno senso per un operatore o amministratore;
- gli attributi dell'operatore mensa non hanno senso per uno studente o amministratore;
- gli attributi dell'amministratore non hanno senso per uno studente o operatore;
- la tabella diventa molto ampia;
- maggiore difficoltà nel garantire vincoli specifici per ruolo;
- soluzione meno pulita dal punto di vista concettuale.

Vincoli necessari:

```text
ruolo IN ('studente', 'operatore_mensa', 'amministratore')
```

Se `ruolo = 'studente'`, allora:

```text
matricola IS NOT NULL
corso_studi IS NOT NULL
anno_corso IS NOT NULL
codice_operatore IS NULL
mansione IS NULL
mensa_id IS NULL
area_responsabilita IS NULL
```

Se `ruolo = 'operatore_mensa'`, allora:

```text
codice_operatore IS NOT NULL
mansione IS NOT NULL
mensa_id IS NOT NULL
matricola IS NULL
corso_studi IS NULL
anno_corso IS NULL
area_responsabilita IS NULL
```

Se `ruolo = 'amministratore'`, allora:

```text
area_responsabilita IS NOT NULL
matricola IS NULL
corso_studi IS NULL
anno_corso IS NULL
codice_operatore IS NULL
mansione IS NULL
mensa_id IS NULL
```

Giudizio: questa alternativa è semplice, ma richiede troppi controlli condizionali. Per esempio, una prenotazione deve essere effettuata solo da uno studente; se la prenotazione puntasse direttamente a `Utente`, bisognerebbe controllare ogni volta che `Utente.ruolo = 'studente'`. Lo stesso problema si avrebbe per i lotti creati dagli operatori. Per questo motivo non è stata scelta.

### Alternativa 2 — Accorpamento del padre nelle entità figlie

In questa alternativa l'entità `Utente` viene eliminata e i suoi attributi vengono duplicati nelle tabelle figlie.

Schema risultante:

```text
Studente(
  id,
  username,
  password,
  nome,
  cognome,
  email,
  matricola,
  corso_studi,
  anno_corso,
  data_registrazione
)

OperatoreMensa(
  id,
  username,
  password,
  nome,
  cognome,
  email,
  codice_operatore,
  mensa_id,
  mansione
)

Amministratore(
  id,
  username,
  password,
  nome,
  cognome,
  email,
  area_responsabilita
)
```

Vantaggi:

- ogni tabella contiene solo attributi coerenti con il proprio ruolo;
- nessun valore `NULL` dovuto alla generalizzazione;
- nessun join necessario per leggere il profilo completo;
- le relazioni possono puntare direttamente a `Studente`, `OperatoreMensa` o `Amministratore`.

Svantaggi:

- ridondanza degli attributi comuni;
- username, password, nome, cognome ed email sono ripetuti in tre tabelle;
- difficoltà nel garantire l'unicità globale di username ed email;
- per ottenere tutti gli utenti è necessario usare una `UNION`;
- soluzione meno adatta al sistema di autenticazione standard di Django.

Vincoli necessari:

- username univoco tra Studente, OperatoreMensa e Amministratore;
- email univoca tra Studente, OperatoreMensa e Amministratore.

Giudizio: questa soluzione elimina i valori nulli, ma introduce ridondanza e problemi di coerenza. Non viene scelta perché Django lavora meglio con un modello utente centralizzato e perché la duplicazione degli attributi comuni renderebbe il sistema meno pulito.


### Scelta effettuata — Alternativa ACCORPAMENTO DELLE ENTITA' FIGLIE NEL PADRE

Tra le due alternative considerate è stata scelta l'**Alternativa 1**, cioè l'accorpamento delle specializzazioni nella tabella generale `Utente`.

La soluzione finale prevede quindi una sola tabella per tutti gli utenti del sistema:

```text
Utente(
  id_utente PK,
  username UNIQUE,
  password,
  nome,
  cognome,
  email UNIQUE,
  ruolo,
  matricola NULL,
  corso_studi NULL,
  anno_corso NULL,
  codice_operatore NULL,
  mansione NULL,
  area_responsabilita NULL,
  id_mensa FK -> Mensa NULL
)
La distinzione tra studente, operatore mensa e amministratore viene gestita tramite il campo ruolo.

Gli attributi specifici vengono utilizzati solo quando sono coerenti con il ruolo dell'utente:

per uno studente vengono valorizzati matricola, corso_studi e anno_corso;
per un operatore mensa vengono valorizzati codice_operatore, mansione e id_mensa;
per un amministratore viene valorizzato area_responsabilita.
Motivazione della scelta

Questa soluzione è stata scelta perché permette di gestire tutti gli utenti in modo centralizzato.

Nel progetto tutti gli utenti devono poter accedere al sistema tramite autenticazione. Avere una sola tabella Utente rende più semplice la gestione di login, credenziali e ruoli.

Rispetto all'Alternativa B, questa scelta evita la duplicazione di dati comuni come username, password, nome, cognome ed email.

Vantaggi:
-tutti gli utenti sono salvati in un'unica tabella;
-le credenziali non vengono duplicate;
-username ed email possono essere resi univoci in modo semplice;
-l'autenticazione è più immediata da gestire;
-il campo ruolo consente di distinguere facilmente i profili;
-la struttura rimane compatta e semplice da interrogare.

Svantaggi:
-alcuni attributi possono assumere valore NULL;
-la tabella Utente contiene campi riferiti a ruoli diversi;
-alcuni vincoli dipendono dal valore del campo ruolo;
-la coerenza tra ruolo e attributi valorizzati deve essere controllata anche dall'applicazione.

**Considerazione finale**

L'Alternativa B avrebbe prodotto tabelle più separate e senza campi inutilizzati, ma avrebbe introdotto ridondanza e maggiore difficoltà nella gestione dell'autenticazione.

Per questo motivo, nel contesto di UniFood Rescue, l'Alternativa A rappresenta il compromesso più adatto: accetta alcuni valori NULL, ma mantiene più semplice la gestione degli utenti e delle credenziali.

La soluzione adottata è quindi:

Utente unica + campo ruolo + attributi specifici opzionali
```
## 6. Modello logico relazionale

```text
Utente(
  id,
  username,
  password,
  first_name,
  last_name,
  email,
  ruolo
)

Studente(
  id,
  utente_id [FK -> Utente, UNIQUE],
  matricola,
  corso_studi,
  anno_corso,
  data_registrazione
)

OperatoreMensa(
  id,
  utente_id [FK -> Utente, UNIQUE],
  mensa_id [FK -> Mensa],
  codice_operatore,
  mansione,
  data_assunzione
)

Amministratore(
  id,
  utente_id [FK -> Utente, UNIQUE],
  area_responsabilita
)

Mensa(
  id,
  nome,
  edificio,
  indirizzo,
  orario_apertura,
  orario_chiusura,
  attiva
)

CategoriaAlimento(
  id,
  nome,
  descrizione
)

ProdottoAlimentare(
  id,
  categoria_id [FK -> CategoriaAlimento],
  nome,
  descrizione,
  vegetariano,
  vegano,
  attivo
)

Allergene(
  id,
  nome,
  descrizione
)

ProdottoAllergene(
  prodotto_id [FK -> ProdottoAlimentare],
  allergene_id [FK -> Allergene]
)

LottoInvenduto(
  id,
  mensa_id [FK -> Mensa],
  prodotto_id [FK -> ProdottoAlimentare],
  operatore_id [FK -> OperatoreMensa],
  quantita_iniziale,
  quantita_disponibile,
  data_pubblicazione,
  data_scadenza,
  ora_inizio_ritiro,
  ora_fine_ritiro,
  prezzo_simbolico,
  stato,
  note
)

Prenotazione(
  id,
  studente_id [FK -> Studente],
  lotto_id [FK -> LottoInvenduto],
  quantita,
  stato,
  data_prenotazione
)

Ritiro(
  id,
  prenotazione_id [FK -> Prenotazione, UNIQUE],
  operatore_id [FK -> OperatoreMensa],
  data_ora_ritiro,
  esito,
  note
)

RecensioneMensa(
  id,
  studente_id [FK -> Studente],
  mensa_id [FK -> Mensa],
  prenotazione_id [FK -> Prenotazione, UNIQUE],
  voto,
  commento,
  data_inserimento
)

Segnalazione(
  id,
  prenotazione_id [FK -> Prenotazione],
  autore_id [FK -> Studente],
  amministratore_id [FK -> Amministratore, NULL],
  titolo,
  descrizione,
  stato,
  esito,
  data_apertura,
  data_chiusura
)


Nota: in Django la relazione molti-a-molti tra `ProdottoAlimentare` e `Allergene` è implementata tramite modello esplicito `ProdottoAllergene`, con vincolo di unicità sulla coppia prodotto-allergene.
```


## 7. Vincoli del sistema

### 7.1 Vincoli sulla generalizzazione

- Ogni `Utente` deve essere associato a uno e un solo profilo tra `Studente`, `OperatoreMensa` e `Amministratore`.
- `Studente.utente_id` deve essere univoco.
- `OperatoreMensa.utente_id` deve essere univoco.
- `Amministratore.utente_id` deve essere univoco.
- Il campo `Utente.ruolo` può assumere solo i valori:
  - `studente`
  - `operatore_mensa`
  - `amministratore`

### 7.2 Vincoli su Mensa e OperatoreMensa

- Ogni `OperatoreMensa` deve essere associato a una `Mensa`.
- Una `Mensa` può avere più operatori.
- Un operatore può creare lotti solo per la mensa a cui è associato.
- Una mensa inattiva non può pubblicare nuovi lotti disponibili.
- L'orario di chiusura deve essere successivo all'orario di apertura.

### 7.3 Vincoli su prodotti, categorie e allergeni

- Ogni `ProdottoAlimentare` deve appartenere a una categoria.
- Una categoria può contenere molti prodotti.
- Un prodotto può avere zero, uno o più allergeni.
- Lo stesso allergene può essere associato a molti prodotti.
- Non deve esistere due volte la stessa associazione prodotto-allergene.
- Il nome di una categoria deve essere univoco.
- Il nome di un allergene deve essere univoco.
- Un prodotto vegano deve essere anche vegetariano.

Vincoli consigliati o implementati:

```text
CategoriaAlimento.nome UNIQUE
Allergene.nome UNIQUE
ProdottoAllergene(prodotto_id, allergene_id) UNIQUE
ProdottoAlimentare(categoria_id, nome) UNIQUE
```

### 7.4 Vincoli sui lotti invenduti

- Ogni lotto deve essere associato a una mensa.
- Ogni lotto deve essere associato a un prodotto alimentare.
- Ogni lotto deve essere creato da un operatore mensa.
- `quantita_iniziale` deve essere maggiore di zero.
- `quantita_disponibile` non può essere negativa.
- `quantita_disponibile` non può essere maggiore di `quantita_iniziale`.
- `data_scadenza` non può essere precedente alla data di pubblicazione.
- `ora_fine_ritiro` deve essere successiva a `ora_inizio_ritiro`.
- Un lotto esaurito, chiuso, scaduto o annullato non può ricevere nuove prenotazioni.
- Un operatore non può creare lotti per una mensa diversa dalla propria.

Stati possibili del lotto:

- `disponibile`
- `esaurito`
- `chiuso`
- `scaduto`
- `annullato`

### 7.5 Vincoli sulle prenotazioni

- Ogni prenotazione deve essere associata a uno studente.
- Ogni prenotazione deve essere associata a un lotto esistente.
- La quantità prenotata deve essere maggiore di zero.
- La quantità prenotata non può superare la quantità disponibile del lotto.
- Uno studente non può prenotare un lotto scaduto.
- Uno studente non può prenotare un lotto annullato.
- Uno studente non può prenotare un lotto chiuso.
- Una prenotazione ritirata non può essere annullata.
- Quando viene creata una prenotazione attiva, la quantità disponibile del lotto diminuisce.
- Quando una prenotazione attiva viene annullata, la quantità viene restituita al lotto.

Esempio:

```text
quantita_disponibile = 8
prenotazione = 2
nuova quantita_disponibile = 6
```

Questa operazione viene gestita in modo atomico, perché riguarda sia la creazione della prenotazione sia l'aggiornamento del lotto.

Stati possibili della prenotazione:

- `attiva`
- `annullata`
- `ritirata`
- `scaduta`

### 7.6 Vincoli sui ritiri

- Ogni ritiro deve riferirsi a una prenotazione.
- Una prenotazione può avere al massimo un ritiro.
- Ogni ritiro deve essere confermato da un operatore mensa.
- Il ritiro può essere confermato solo se la prenotazione è attiva.
- Dopo il ritiro, la prenotazione passa allo stato `ritirata` se l'esito è `consegnato`.
- L'operatore può confermare solo ritiri relativi alla propria mensa.

Esiti possibili del ritiro:

- `consegnato`
- `non_consegnato`
- `annullato`

### 7.7 Vincoli sulle recensioni

- Una recensione deve essere scritta da uno studente.
- Una recensione deve riferirsi a una mensa.
- Una recensione deve essere collegata a una prenotazione.
- Lo studente può recensire una mensa solo dopo un ritiro completato.
- Il voto deve essere compreso tra 1 e 5.
- Uno studente non può recensire due volte la stessa prenotazione.
- La recensione deve riguardare la mensa associata al lotto prenotato.

ESEMPIO CONCRETO: 

```text
voto BETWEEN 1 AND 5
UNIQUE(prenotazione_id)
```

### 7.8 Vincoli sulle segnalazioni

- Una segnalazione deve essere associata a una prenotazione esistente.
- L'autore della segnalazione deve essere lo studente che ha effettuato la prenotazione.
- L'amministratore può essere `NULL` finché la segnalazione non viene presa in carico.
- Lo stato della segnalazione può assumere solo valori previsti.
- `data_chiusura` viene valorizzata quando la segnalazione entra in uno stato finale.
- Per chiudere una segnalazione serve un esito.

Stati possibili della segnalazione:

- `aperta`
- `in_carico`
- `risolta`
- `respinta`
- `chiusa`

---

## 9. Stati del dominio

### 9.1 Stati del LottoInvenduto

| Stato | Significato |
|---|---|
| `disponibile` | Il lotto è visibile agli studenti e può essere prenotato. |
| `esaurito` | La quantità disponibile è arrivata a zero. |
| `chiuso` | L'operatore ha chiuso manualmente il lotto. |
| `scaduto` | La data di scadenza o la fascia utile sono superate. |
| `annullato` | Il lotto è stato annullato per errore o problema operativo. |

### 9.2 Stati della Prenotazione

| Stato | Significato |
|---|---|
| `attiva` | La prenotazione è valida e il prodotto deve ancora essere ritirato. |
| `annullata` | La prenotazione è stata annullata. |
| `ritirata` | Lo studente ha ritirato il prodotto e l'operatore ha confermato il ritiro. |
| `scaduta` | La prenotazione non è stata ritirata entro la fascia prevista. |

### 9.3 Stati della Segnalazione

| Stato | Significato |
|---|---|
| `aperta` | La segnalazione è stata creata ma non ancora gestita. |
| `in_carico` | Un amministratore ha preso in carico la segnalazione. |
| `risolta` | Il problema è stato gestito positivamente. |
| `respinta` | La segnalazione è stata valutata non fondata. |
| `chiusa` | La segnalazione è conclusa definitivamente. |

---

## 10. Scelte progettuali rilevanti

### 10.1 LottoInvenduto come entità centrale

La scelta più importante del progetto è modellare il `LottoInvenduto` come entità autonoma.

Il lotto non coincide con il prodotto alimentare.

```text
ProdottoAlimentare = Pasta al pomodoro
LottoInvenduto = 8 porzioni di Pasta al pomodoro disponibili oggi alla Mensa Centrale dalle 17:00 alle 18:00
```

Questa separazione è fondamentale perché lo stesso prodotto può essere presente in molti lotti diversi, in giorni diversi, in mense diverse e con quantità diverse.

Senza questa distinzione, il sistema sarebbe una semplice lista di pasti. Con questa distinzione, invece, diventa un sistema informativo capace di gestire disponibilità concrete, temporanee e tracciabili.

### 10.2 Separazione tra ProdottoAlimentare e LottoInvenduto

`ProdottoAlimentare` descrive il tipo di alimento.

`LottoInvenduto` descrive una disponibilità concreta e temporanea.

Questa scelta permette di evitare duplicazioni. Senza questa separazione, ogni volta che viene pubblicato un lotto bisognerebbe reinserire anche tutte le informazioni del prodotto: nome, descrizione, categoria, allergeni, caratteristiche vegetariane o vegane.

Separando le due entità, il prodotto viene registrato una sola volta e può essere riutilizzato in più lotti.

### 10.3 Gestione molti-a-molti degli allergeni

Gli allergeni non vengono salvati come campi booleani dentro `ProdottoAlimentare`.

Non si usa:

```text
contiene_glutine
contiene_lattosio
contiene_uova
contiene_soia
```

Si usa invece:

```text
Allergene
ProdottoAllergene
```

Questa scelta è migliore perché:

- un prodotto può contenere più allergeni;
- un allergene può essere presente in più prodotti;
- il sistema è più estendibile;
- se viene aggiunto un nuovo allergene non bisogna modificare la struttura della tabella prodotto;
- le ricerche per allergene diventano più flessibili.

Dal punto di vista del progetto di basi di dati, questa relazione è significativa perché introduce una classica relazione molti-a-molti risolta tramite tabella associativa.

### 10.4 Quantità disponibile salvata nel lotto

Il campo `quantita_disponibile` viene salvato direttamente nel lotto.

Questa è una piccola ridondanza controllata, perché teoricamente la quantità disponibile potrebbe essere calcolata così:

```text
quantita_disponibile = quantita_iniziale - somma(prenotazioni attive/ritirate)
```

Tuttavia, per semplicità implementativa e chiarezza applicativa, viene mantenuto un campo dedicato.

Questa scelta richiede un vincolo applicativo: quando si crea o annulla una prenotazione, `quantita_disponibile` deve essere aggiornata correttamente.

Per evitare inconsistenze, l'aggiornamento viene gestito in transazione atomica.

### 10.5 Nessuna gestione dei pagamenti online

Il progetto non gestisce pagamenti reali.

Il campo `prezzo_simbolico` è solo informativo.

Questa scelta evita complessità inutili come:

- integrazione con sistemi di pagamento;
- ricevute;
- rimborsi;
- transazioni economiche;
- dati sensibili;
- gestione fiscale.

Il focus rimane sul database e sulla gestione dei processi informativi.

### 10.6 Ritiro come entità autonoma

Il ritiro viene modellato come entità separata da `Prenotazione`.

Questa scelta è importante perché:

- una prenotazione può esistere senza essere ancora ritirata;
- il ritiro ha dati propri: operatore, data/ora, esito e note;
- si può distinguere tra prenotazione attiva e ritiro completato;
- si mantiene uno storico preciso delle consegne effettivamente avvenute.

Se il ritiro fosse solo uno stato della prenotazione, si perderebbero informazioni importanti sull'operatore che ha confermato la consegna e sull'esito del ritiro.

### 10.7 Recensione vincolata al ritiro

La recensione può essere lasciata solo dopo un ritiro completato.

Questa scelta evita recensioni non motivate da un'esperienza reale. Uno studente può valutare una mensa solo se ha effettivamente prenotato e ritirato un lotto presso quella mensa.

### 12.8 Segnalazioni collegate alla prenotazione

La segnalazione viene collegata alla prenotazione, non direttamente alla mensa o al prodotto.

Questa scelta è utile perché una prenotazione identifica già:

- lo studente;
- il lotto;
- la mensa;
- il prodotto;
- la quantità;
- lo stato;
- l'eventuale ritiro.

In questo modo ogni segnalazione è contestualizzata e può essere analizzata dall'amministratore con tutti i dati necessari.

### 10.9 Ruoli separati e controlli applicativi

La presenza di tre ruoli rende il sistema più realistico:

- lo studente non deve poter creare lotti;
- l'operatore non deve poter gestire segnalazioni amministrative di sistema;
- l'amministratore non partecipa direttamente al processo di prenotazione e ritiro, ma supervisiona il sistema.

Questa separazione permette di dimostrare competenze non solo nella progettazione del database, ma anche nella gestione dei permessi applicativi.

### 10.10 Dashboard e statistiche come valore informativo

La dashboard non è solo un elemento grafico, ma rappresenta una parte importante del sistema informativo.

Attraverso le statistiche si possono monitorare:

- numero di lotti pubblicati;
- numero di porzioni prenotate;
- numero di porzioni ritirate;
- quantità recuperate per mensa;
- segnalazioni aperte;
- valutazione media delle mense.

Questi dati mostrano il valore del sistema: non solo registrare operazioni, ma trasformarle in informazioni utili.

---

## 11. Query SQL significative

### 11.1 Ricerca dei lotti disponibili per mensa

```sql
SELECT l.id, p.nome, l.quantita_disponibile, l.ora_inizio_ritiro, l.ora_fine_ritiro
FROM LottoInvenduto l
JOIN ProdottoAlimentare p ON l.prodotto_id = p.id
JOIN Mensa m ON l.mensa_id = m.id
WHERE m.nome = 'Mensa Centrale'
AND l.stato = 'disponibile'
AND l.quantita_disponibile > 0;
```

### 11.2 Ricerca dei lotti che non contengono un certo allergene

Esempio: prodotti senza lattosio.

```sql
SELECT DISTINCT l.id, p.nome, m.nome AS mensa, l.quantita_disponibile
FROM LottoInvenduto l
JOIN ProdottoAlimentare p ON l.prodotto_id = p.id
JOIN Mensa m ON l.mensa_id = m.id
WHERE l.stato = 'disponibile'
AND l.quantita_disponibile > 0
AND p.id NOT IN (
    SELECT pa.prodotto_id
    FROM ProdottoAllergene pa
    JOIN Allergene a ON pa.allergene_id = a.id
    WHERE a.nome = 'Lattosio'
);
```

### 11.3 Storico prenotazioni di uno studente

```sql
SELECT pr.id, p.nome, m.nome AS mensa, pr.quantita, pr.stato, pr.data_prenotazione
FROM Prenotazione pr
JOIN LottoInvenduto l ON pr.lotto_id = l.id
JOIN ProdottoAlimentare p ON l.prodotto_id = p.id
JOIN Mensa m ON l.mensa_id = m.id
WHERE pr.studente_id = 1
ORDER BY pr.data_prenotazione DESC;
```

### 11.4 Prenotazioni da ritirare per una mensa

```sql
SELECT pr.id, u.first_name, u.last_name, p.nome, pr.quantita
FROM Prenotazione pr
JOIN Studente s ON pr.studente_id = s.id
JOIN Utente u ON s.utente_id = u.id
JOIN LottoInvenduto l ON pr.lotto_id = l.id
JOIN ProdottoAlimentare p ON l.prodotto_id = p.id
WHERE l.mensa_id = 1
AND pr.stato = 'attiva';
```

### 11.5 Porzioni recuperate per mensa

```sql
SELECT m.nome, SUM(pr.quantita) AS porzioni_ritirate
FROM Ritiro r
JOIN Prenotazione pr ON r.prenotazione_id = pr.id
JOIN LottoInvenduto l ON pr.lotto_id = l.id
JOIN Mensa m ON l.mensa_id = m.id
WHERE pr.stato = 'ritirata'
GROUP BY m.nome;
```

### 11.6 Media recensioni per mensa

```sql
SELECT m.nome, AVG(rm.voto) AS voto_medio
FROM RecensioneMensa rm
JOIN Mensa m ON rm.mensa_id = m.id
GROUP BY m.nome;
```

### 11.7 Segnalazioni aperte o in carico

```sql
SELECT s.id, s.titolo, s.stato, s.data_apertura
FROM Segnalazione s
WHERE s.stato IN ('aperta', 'in_carico')
ORDER BY s.data_apertura ASC;
```

### 11.8 Lotti più richiesti

```sql
SELECT p.nome, COUNT(pr.id) AS numero_prenotazioni
FROM Prenotazione pr
JOIN LottoInvenduto l ON pr.lotto_id = l.id
JOIN ProdottoAlimentare p ON l.prodotto_id = p.id
GROUP BY p.nome
ORDER BY numero_prenotazioni DESC;
```

### 11.9 Quantità non recuperata stimata

```sql
SELECT m.nome, SUM(l.quantita_disponibile) AS quantita_non_ritirata
FROM LottoInvenduto l
JOIN Mensa m ON l.mensa_id = m.id
WHERE l.stato IN ('scaduto', 'chiuso')
GROUP BY m.nome;
```

---



## 11. Struttura del repository

```text
.
├── unifoodrescue/              # configurazione Django del progetto
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── mensa/                      # app principale
│   ├── models.py               # modello dati e vincoli applicativi
│   ├── views.py                # viste pubbliche, studente, operatore, amministratore
│   ├── forms.py                # form Django
│   ├── urls.py                 # routing dell'app
│   ├── permissions.py          # controlli sui ruoli
│   ├── admin.py                # configurazione admin Django
│   ├── tests.py                # test automatici
│   └── migrations/
│
├── templates/                  # template HTML Django
│   ├── base.html
│   ├── mensa/
│   └── registration/
│
├── static/css/                 # stile CSS personalizzato
│   └── style.css
│
├── fixtures/                   # dati iniziali di esempio
│   └── initial_data.json
│
├── docs/                       # documentazione tecnica
│   ├── relazione.md
│   ├── er_diagram.mmd
│   ├── query_significative.sql
│   └── security_bonus.md
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 18. Organizzazione delle pagine

### 18.1 Area pubblica

- Home page
- Catalogo lotti disponibili
- Dettaglio lotto
- Login
- Registrazione

### 18.2 Area studente

- Dashboard studente
- Profilo personale
- Catalogo lotti
- Dettaglio lotto
- Prenota lotto
- Le mie prenotazioni
- Annulla prenotazione attiva
- Storico ritiri
- Recensioni lasciate
- Apri segnalazione

### 18.3 Area operatore mensa

- Dashboard operatore
- Crea nuovo lotto
- Gestisci lotti della mensa
- Modifica lotto
- Chiudi lotto
- Prenotazioni da ritirare
- Conferma ritiro
- Storico ritiri confermati

### 18.4 Area amministratore

- Dashboard amministratore
- Gestione mense
- Gestione categorie
- Gestione prodotti
- Gestione allergeni
- Gestione segnalazioni
- Statistiche recupero alimentare

### 18.5 Area admin Django

- Gestione utenti
- Gestione studenti
- Gestione operatori
- Gestione amministratori
- Gestione mense
- Gestione prodotti
- Gestione allergeni
- Gestione lotti
- Gestione prenotazioni
- Gestione ritiri
- Gestione recensioni
- Gestione segnalazioni

---

## 19. Requisiti implementativi coperti

Il progetto copre i requisiti principali richiesti da una consegna di sistema informativo:

| Requisito | Stato | Dove si trova |
|---|---:|---|
| Analisi del dominio | Coperto | README + `docs/relazione.md` |
| Modello E-R | Coperto | README + `docs/er_diagram.mmd` |
| Generalizzazione/specializzazione | Coperto | Utente -> Studente / OperatoreMensa / Amministratore |
| Progettazione logica | Coperto | README + modelli Django |
| Vincoli di integrità | Coperto | `models.py`, form, viste, transazioni |
| Backend Django | Coperto | progetto `unifoodrescue`, app `mensa` |
| Template Django | Coperto | cartella `templates/` |
| Bootstrap CSS | Coperto | template + `static/css/style.css` |
| JavaScript non necessario | Coperto | applicazione basata su backend e template |
| Dati di esempio / dump | Coperto | `fixtures/initial_data.json` |
| Istruzioni di avvio | Coperto | sezione installazione |
| Query significative | Coperto | README + `docs/query_significative.sql` |
| Bonus sicurezza | Coperto | README + `docs/security_bonus.md` |

Funzionalità minime effettivamente coperte:

1. Modelli Django per tutte le entità principali.
2. Autenticazione con distinzione tra studenti, operatori mensa e amministratori.
3. CRUD delle mense.
4. CRUD dei prodotti alimentari.
5. Gestione categorie e allergeni.
6. Associazione prodotti-allergeni.
7. Creazione lotti da parte dell'operatore mensa.
8. Ricerca e visualizzazione dei lotti disponibili.
9. Prenotazione di un lotto da parte dello studente.
10. Aggiornamento automatico della quantità disponibile.
11. Conferma del ritiro da parte dell'operatore.
12. Storico prenotazioni dello studente.
13. Recensioni dopo ritiro completato.
14. Apertura e gestione segnalazioni.
15. Dashboard riepilogativa con statistiche semplici.

---

## 20. Bonus sicurezza

### 20.1 Simulazione SQL injection

Una possibile simulazione riguarda la ricerca dei lotti o dei prodotti.

Codice vulnerabile:

```python
query = "SELECT * FROM ProdottoAlimentare WHERE nome LIKE '%" + ricerca + "%'"
```

Questo codice è pericoloso perché concatena direttamente l'input dell'utente nella query SQL.

Un utente malevolo potrebbe inserire un input appositamente costruito per alterare la query.

Esempio:

```text
' OR '1'='1
```

In questo modo la query potrebbe restituire più risultati del previsto o aggirare alcuni filtri.

Prevenzione con Django ORM:

```python
ProdottoAlimentare.objects.filter(nome__icontains=ricerca)
```

In questo modo l'input dell'utente non viene concatenato manualmente alla query SQL. Il framework gestisce automaticamente la costruzione sicura della query.

### 20.2 Simulazione brute-force

Un secondo esempio di attacco riguarda il login.

Un attaccante potrebbe provare molte password diverse per lo stesso account, tentando di indovinare le credenziali di uno studente, di un operatore mensa o di un amministratore.

Misure di prevenzione:

- password robuste;
- hash delle password;
- limitazione dei tentativi di login;
- logging dei tentativi falliti;
- uso del sistema di autenticazione Django;
- messaggi di errore generici;
- protezione CSRF nei form.

Il sistema di autenticazione di Django è adatto al progetto perché gestisce già hashing delle password, sessioni utente e protezione dei form.

### 20.3 Protezioni applicative usate nel progetto

- Uso dell'ORM Django invece di query SQL concatenate manualmente.
- Uso di `transaction.atomic()` per operazioni critiche su prenotazioni e quantità.
- Uso di `select_for_update()` per ridurre il rischio di race condition nella prenotazione dei lotti.
- Controlli sui ruoli tramite funzioni di permesso.
- Vincoli nei modelli tramite `clean()` e validatori Django.
- Protezione CSRF nativa nei form Django.

---

## 21. Considerazioni finali

**UniFood Rescue** rappresenta un sistema informativo completo e coerente con gli obiettivi di un progetto di Basi di Dati.

Il dominio scelto permette di modellare:

- utenti con ruoli differenti;
- una generalizzazione/specializzazione significativa;
- relazioni uno-a-molti;
- relazioni molti-a-molti;
- vincoli di integrità;
- stati applicativi;
- storico delle prenotazioni;
- gestione dei ritiri;
- gestione degli allergeni;
- recensioni;
- segnalazioni;
- dashboard statistiche;
- monitoraggio delle quantità recuperate.

Il progetto è sufficientemente semplice da essere implementato con Django e SQLite, ma abbastanza ricco da mostrare competenze di progettazione concettuale, logica e applicativa.

Il cuore del sistema è il seguente flusso:

```text
OperatoreMensa -> LottoInvenduto -> Prenotazione -> Ritiro -> Recensione / Segnalazione
```

Questa struttura rende il progetto chiaro, scalabile e collegato al tema del recupero delle eccedenze alimentari.

Dal punto di vista dei dati, le parti più interessanti sono:

- `ProdottoAlimentare` <-> `Allergene`
- `Mensa` -> `LottoInvenduto`
- `LottoInvenduto` -> `Prenotazione`
- `Prenotazione` -> `Ritiro`
- `Prenotazione` -> `Segnalazione`
- `Mensa` -> `RecensioneMensa`

La scelta di modellare `LottoInvenduto` come entità centrale rende il progetto più forte rispetto a una semplice piattaforma di prenotazione pasti, perché consente di gestire quantità, disponibilità, scadenza, mensa, prodotto, stato e tracciabilità.

La presenza della relazione molti-a-molti tra prodotti e allergeni arricchisce ulteriormente il modello E-R e rende il sistema più realistico.

Inoltre, l'introduzione di prenotazioni, ritiri, recensioni e segnalazioni permette di modellare un ciclo di vita completo del dato: dalla pubblicazione del lotto fino alla sua effettiva consegna o alla gestione di eventuali problemi.

In conclusione, **UniFood Rescue** non è solo un'applicazione per prenotare cibo: è un sistema informativo che organizza un processo reale, riduce lo spreco, traccia le operazioni e trasforma dati semplici in informazioni utili per studenti, operatori e amministratori.
