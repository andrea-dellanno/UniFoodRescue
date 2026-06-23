# UniFood Rescue

> Sistema Django per la gestione e il recupero delle eccedenze alimentari nelle mense universitarie.

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
- [5. Generalizzazione e specializzazione](#5-generalizzazione-e-specializzazione)
- [6. Modello logico relazionale](#6-modello-logico-relazionale)
- [7. Vincoli del sistema](#7-vincoli-del-sistema)
- [8. Stati del dominio](#8-stati-del-dominio)
- [9. Scelte progettuali rilevanti](#9-scelte-progettuali-rilevanti)
- [10. Query SQL significative](#10-query-sql-significative)
- [11. Struttura del repository](#11-struttura-del-repository)
- [12. Organizzazione delle pagine](#12-organizzazione-delle-pagine)
- [13. Bonus sicurezza](#14-bonus-sicurezza)
- [14. Considerazioni finali](#15-considerazioni-finali)

---

## 1. Descrizione del progetto

**UniFood Rescue** è un'applicazione web pensata per un contesto universitario, finalizzata alla gestione e al recupero delle eccedenze alimentari prodotte dalle mense universitarie.

Il processo reale è il seguente: a fine servizio una mensa può avere prodotti alimentari ancora disponibili. Questi prodotti non vengono trattati come pasti generici, ma come **lotti invenduti**, cioè disponibilità concrete associate a:

- una mensa precisa;
- un prodotto alimentare preciso;
- una quantità iniziale;
- una quantità ancora disponibile;
- una data di ritiro;
- una fascia oraria di ritiro;
- uno stato operativo;
- un operatore responsabile della pubblicazione;
- un codice lotto univoco e leggibile.

Nel sistema ogni lotto viene identificato tramite un codice breve del tipo:

```text
L-0001
L-0002
L-0003
```

Il prefisso `L` indica il lotto. Il codice non è inserito manualmente dall'operatore, ma viene generato automaticamente a partire dall'identificativo del lotto. Non sono previsti codici separati per ritiro, prenotazione o pubblicazione: il codice visibile è unico ed è sempre associato al lotto.

La piattaforma prevede tre tipologie principali di utenti:

- **Studenti**: consultano i lotti disponibili, prenotano prodotti, visualizzano le proprie prenotazioni, lasciano recensioni e aprono segnalazioni.
- **Operatori mensa**: pubblicano lotti invenduti, modificano le disponibilità, chiudono lotti, visualizzano i ritiri da confermare e registrano i ritiri completati.
- **Amministratori**: gestiscono mense, categorie, allergeni, prodotti, statistiche e segnalazioni.

Il sistema non prevede pagamenti online, consegne a domicilio, QR code obbligatori o funzionalità mobile complesse.


---

## 2. Obiettivo del sistema

Il sistema nasce con l'obiettivo di supportare le mense universitarie nella gestione organizzata delle eccedenze alimentari giornaliere.

Senza un sistema strutturato, queste eccedenze rischiano di essere eliminate, gestite informalmente o distribuite senza tracciabilità.

La logica principale non è quella della vendita, ma quella della **tracciabilità**. Il sistema deve rispondere a domande come:

- quale mensa ha pubblicato un certo lotto?
- quale prodotto è stato reso disponibile?
- quali allergeni contiene?
- quante porzioni sono ancora prenotabili?
- quale studente ha prenotato?
- il lotto è futuro, pronto al ritiro, ritirato o non ritirato?
- il ritiro è stato effettivamente confermato dall'operatore?
- ci sono state recensioni o segnalazioni?

Un aspetto importante è la coerenza tra quantità iniziale, quantità disponibile e prenotazioni effettuate.

Esempio:

```text
Lotto L-0001
quantità iniziale = 8

Mario Rossi prenota 1 porzione
Mario Rossi prenota altre 2 porzioni ma non le ritira

quantità non più disponibile = 3
quantità disponibile = 5

risultato visualizzato:
5/8 disponibili
```

Il valore `5/8` è quindi giustificato dalle prenotazioni collegate al lotto, comprese quelle ritirate e quelle non ritirate.

---

## 3. Funzionalità implementate

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
11. Limite massimo di prenotazione pari a 99 porzioni per volta.
12. Aggiornamento automatico della quantità disponibile del lotto quando viene effettuata una prenotazione.
13. Annullamento di una prenotazione attiva da parte dello studente con restituzione della quantità al lotto.
14. Visualizzazione dello storico delle prenotazioni dello studente.
15. Visualizzazione dello stato interfaccia della prenotazione:
    - ritiro programmato;
    - pronta da ritirare;
    - ritirata;
    - non ritirata;
    - annullata.
16. Area operatore dedicata, distinta dall'area studente.
17. Home operatore come dashboard operativa della mensa.
18. Visualizzazione dei ritiri da confermare da parte dell'operatore.
19. Conferma diretta del ritiro tramite azione "Segna ritirata", senza pagina intermedia non necessaria.
20. Passaggio automatico a `non_ritirata` per prenotazioni attive non confermate entro la fine della fascia di ritiro.
21. Gestione degli stati del lotto e della prenotazione.
22. Inserimento di recensioni sulla mensa dopo un ritiro completato.
23. Voto recensione obbligatorio, vincolato da 1 a 5.
24. Commento recensione opzionale con placeholder esplicativo.
25. Apertura di segnalazioni relative a prenotazioni problematiche.
26. Presa in carico e gestione delle segnalazioni da parte dell'amministratore.
27. Dashboard riepilogative per studente, operatore e amministratore.
28. Area admin Django per la gestione completa dei dati.

---

## 4. Flusso principale

Il flusso principale dell'applicazione è il seguente:

1. Un operatore mensa accede alla piattaforma.
2. L'operatore pubblica un lotto invenduto selezionando un prodotto alimentare già registrato.
3. Il sistema associa automaticamente il lotto alla mensa dell'operatore.
4. L'operatore inserisce la quantità disponibile, la data e la fascia oraria di ritiro.
5. Alla pubblicazione, la quantità iniziale viene impostata uguale alla quantità disponibile inserita.
6. Il lotto viene pubblicato nello stato `disponibile`.
7. Uno studente accede al catalogo dei lotti disponibili.
8. Lo studente filtra i lotti in base a mensa, categoria, allergeni o caratteristiche alimentari.
9. Lo studente prenota una quantità del lotto.
10. Il sistema controlla che il lotto sia disponibile, non scaduto e con quantità sufficiente.
11. Se la prenotazione è valida, il sistema riduce automaticamente la quantità disponibile del lotto.
12. Se il ritiro è futuro, la prenotazione viene mostrata come `Ritiro programmato`.
13. Quando arriva la fascia oraria di ritiro, la prenotazione viene mostrata allo studente come `Pronta da ritirare`.
14. Nella stessa fascia oraria, l'operatore vede la prenotazione come `In attesa di ritiro`.
15. L'operatore può segnare direttamente la prenotazione come ritirata.
16. La prenotazione passa allo stato `ritirata`.
17. Se la fascia oraria termina senza conferma, la prenotazione attiva passa automaticamente allo stato `non_ritirata`.
18. Lo studente può lasciare una recensione sulla mensa solo dopo un ritiro completato.
19. In caso di problema, lo studente può aprire una segnalazione.
20. L'amministratore può prendere in carico la segnalazione e chiuderla con un esito.

In forma sintetica:

```text
OperatoreMensa -> LottoInvenduto -> Prenotazione -> Ritiro confermato / Non ritiro automatico -> Recensione / Segnalazione
```

Questo flusso rappresenta il ciclo di vita completo del dato: dalla pubblicazione dell'eccedenza fino alla sua consegna effettiva o alla gestione di eventuali problemi.

---

## 5. Generalizzazione e specializzazione

Il sistema prevede una gerarchia di generalizzazione con entità padre `Utente` e tre specializzazioni:

- `Studente`
- `OperatoreMensa`
- `Amministratore`

La generalizzazione è:

- **totale**, perché ogni utente registrato deve essere necessariamente uno studente, un operatore mensa o un amministratore;
- **disgiunta**, perché un utente non può appartenere contemporaneamente a più ruoli.

Nel ragionamento concettuale sono state considerate due possibili trasformazioni.

---

### Alternativa 1 — Accorpamento del padre nelle entità figlie

In questa alternativa l'entità `Utente` viene eliminata e i suoi attributi comuni (nome, cognome, mail, password) vengono replicati in ciascuna delle entità figlie.

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
  mansione,
  data_assunzione
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

- ogni entità contiene solo attributi coerenti con il proprio ruolo;
- non ci sono campi non valorizzati dovuti alla generalizzazione;
- le relazioni possono puntare direttamente a `Studente`, `OperatoreMensa` o `Amministratore`;
- la separazione concettuale tra i ruoli è molto chiara.

Svantaggi:

- gli attributi comuni vengono duplicati;
- `username`, `password`, `nome`, `cognome` ed `email` sono ripetuti in più entità;
- diventa più difficile garantire l'unicità globale di username ed email;
- la gestione dell'autenticazione è meno centralizzata;
- per ottenere tutti gli utenti della piattaforma sarebbe necessario unire più insiemi di dati;
- la soluzione è meno adatta a un'applicazione Django basata su un modello utente centrale.

Questa alternativa è utile se si vuole privilegiare la separazione netta tra ruoli ed evitare attributi non utilizzati. Tuttavia, introduce ridondanza negli attributi comuni degli account.

---

### Alternativa 2 — Accorpamento delle entità figlie nel padre

In questa alternativa si mantiene una sola entità `Utente`, nella quale vengono mantenuti gli attributi comuni di Utente e aggiunti quelli specifici di ogni singolo ruolo.

L'attributo fondamentale è:

```text
ruolo ∈ {studente, operatore_mensa, amministratore}
```

Il ruolo non viene considerato un semplice attributo descrittivo, ma un **attributo discriminante**. Esso determina il tipo dell'utente e vincola i suoi permessi e le azioni abilitate.

Vincoli sul ruolo:

```text
ruolo = studente:
PRENOTAZIONE, RECENSIONE, APERTURA

ruolo = operatore_mensa:
PUBBLICAZIONE, ASSEGNAZIONE

ruolo = amministratore:
GESTIONE
```

Schema concettuale risultante:

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
  data_registrazione,
  codice_operatore,
  mansione,
  data_assunzione,
  mensa_id,
  area_responsabilita
)
```

Vantaggi:

- tutti gli utenti sono gestiti tramite un'unica entità;
- username, password ed email non vengono duplicati;
- l'autenticazione è centralizzata;
- il ruolo permette di distinguere le funzionalità disponibili;
- l'unicità di username ed email è più semplice da garantire;
- la struttura rispecchia meglio il fatto che tutti gli attori accedono alla stessa piattaforma.

Svantaggi:

- alcuni attributi specifici possono essere nulli;
- l'entità `Utente` diventa più ampia;
- servono vincoli basati sul valore di `ruolo`;
- la coerenza tra ruolo e attributi valorizzati deve essere controllata anche dall'applicazione.

---

### Scelta effettuata — Accorpamento delle entità figlie nel padre

Tra le due alternative considerate è stata scelta l'**Alternativa 2**, cioè l'accorpamento delle specializzazioni nell'entità generale `Utente`.

Il ruolo è un attributo fondamentale, perché determina il comportamento dell'utente nel sistema. Tuttavia, poiché studenti, operatori e amministratori condividono lo stesso meccanismo di accesso, si è preferito mantenerli all'interno dell'unica entità `Utente`, usando `ruolo` come attributo discriminante.

Quindi, `Utente` rappresenta l'identità di accesso comune, mentre l'attributo `ruolo` permette di distinguere le funzionalità disponibili.

Questa scelta evita la duplicazione di dati comuni come:

- username;
- password;
- nome;
- cognome;
- email.

Accetta invece la presenza di alcuni attributi specifici NULL per tutti i ruoli.

La soluzione adottata dal punto di vista concettuale è quindi:

```text
Utente unica + campo ruolo + attributi specifici condizionati dal ruolo
```

Dal punto di vista implementativo Django, il progetto mantiene comunque una struttura coerente con l'autenticazione centralizzata: `Utente` rimane il modello principale di account, mentre i profili specifici (`Studente`, `OperatoreMensa`, `Amministratore`) sono collegati tramite relazione uno-a-uno. Questa scelta consente di conservare il vantaggio dell'account unico, mantenendo al tempo stesso più ordinati gli attributi specifici dei ruoli.

---

## 6. Modello logico relazionale

```text
UTENTE(i̲d̲_̲u̲t̲e̲n̲t̲e̲, username, password, first_name, last_name, email, ruolo, matricola, corso_studi, anno_corso, data_registrazione, codice_operatore, mansione, data_assunzione, area_responsabilita, id_mensa: MENSA)

MENSA(i̲d̲_̲m̲e̲n̲s̲a̲, nome, edificio, indirizzo, orario_apertura, orario_chiusura, attiva)

PRENOTAZIONE(i̲d̲_̲p̲r̲e̲n̲o̲t̲a̲z̲i̲o̲n̲e̲, id_studente: UTENTE, id_lotto: LOTTO_INVENDUTO, quantita, stato, data_prenotazione, esito_ritiro, data_ora_ritiro)

LOTTO_INVENDUTO(i̲d̲_̲l̲o̲t̲t̲o̲, id_mensa: MENSA, id_prodotto: PRODOTTO_ALIMENTARE, id_operatore: UTENTE, quantita_iniziale, quantita_disponibile, data_pubblicazione, data_scadenza, ora_inizio_ritiro, ora_fine_ritiro, prezzo_simbolico, stato, note)

PRODOTTO_ALIMENTARE(i̲d̲_̲p̲r̲o̲d̲o̲t̲t̲o̲, nome, descrizione, vegetariano, vegano, attivo)

ALLERGENE(i̲d̲_̲a̲l̲l̲e̲r̲g̲e̲n̲e̲, nome, descrizione)

CONTENUTO(i̲d̲_̲p̲r̲o̲d̲o̲t̲t̲o̲:̲ ̲P̲R̲O̲D̲O̲T̲T̲O̲_̲A̲L̲I̲M̲E̲N̲T̲A̲R̲E̲, i̲d̲_̲a̲l̲l̲e̲r̲g̲e̲n̲e̲:̲ ̲A̲L̲L̲E̲R̲G̲E̲N̲E̲)

RECENSIONE(i̲d̲_̲r̲e̲c̲e̲n̲s̲i̲o̲n̲e̲, id_studente: UTENTE, id_mensa: MENSA, id_prenotazione: PRENOTAZIONE, voto, commento, data_inserimento)

SEGNALAZIONE(i̲d̲_̲s̲e̲g̲n̲a̲l̲a̲z̲i̲o̲n̲e̲, id_prenotazione: PRENOTAZIONE, id_autore: UTENTE, id_amministratore: UTENTE, titolo, descrizione, stato, esito, data_apertura, data_chiusura)
```

Nota: in Django la relazione molti-a-molti tra `ProdottoAlimentare` e `Allergene` è implementata tramite modello esplicito `ProdottoAllergene`, con vincolo di unicità sulla coppia prodotto-allergene.

---

## 7. Vincoli del sistema

### 7.1 Vincoli su Utente

- Ogni `Utente` possiede un solo ruolo.
- Il campo `Utente.ruolo` può assumere solo i valori:
  - `studente`
  - `operatore_mensa`
  - `amministratore`
- Il ruolo determina quali operazioni l'utente può eseguire.
- Solo uno studente può prenotare lotti, scrivere recensioni e aprire segnalazioni.
- Solo un operatore mensa può pubblicare lotti ed essere assegnato a una mensa.
- Solo un amministratore può gestire segnalazioni amministrative.
- `Studente.utente_id` deve essere univoco.
- `OperatoreMensa.utente_id` deve essere univoco.
- `Amministratore.utente_id` deve essere univoco.

### 7.2 Vincoli sui lotti invenduti

- Ogni lotto deve essere associato a una mensa.
- Ogni lotto deve essere associato a un prodotto alimentare.
- Ogni lotto deve essere pubblicato da un operatore mensa.
- Il codice lotto è generato automaticamente in forma breve, ad esempio `L-0001`.
- `quantita_iniziale` deve essere maggiore di zero.
- `quantita_disponibile` non può essere negativa.
- `quantita_disponibile` non può essere maggiore di `quantita_iniziale`.
- `data_scadenza` non può essere precedente alla data di pubblicazione.
- `ora_fine_ritiro` deve essere successiva a `ora_inizio_ritiro`.
- Un lotto esaurito, chiuso, scaduto o annullato non può ricevere nuove prenotazioni.
- Un operatore non può pubblicare lotti per una mensa diversa dalla propria.
- Il lotto è nello stato `disponibile` se la finestra di ritiro è valida ed attuale e la quantità è maggiore di zero.
- La quantità disponibile è modificabile dall'operatore, ma non può superare la quantità iniziale.

Stati possibili del lotto:

- `disponibile`
- `esaurito`
- `chiuso`
- `scaduto`
- `annullato`
- 
### 7.3 Vincoli su Mensa e OperatoreMensa

- Ogni `OperatoreMensa` deve essere associato a una `Mensa`.
- Una `Mensa` può avere più operatori.
- Un operatore può pubblicare lotti solo per la mensa a cui è associato.

### 7.4 Vincoli su prodotti e allergeni

- Un prodotto può avere zero, uno o più allergeni.
- Lo stesso allergene può essere contenuto in più prodotti.
- Il nome di un allergene è il suo identificativo e deve essere univoco.

Vincoli implementati:

```text
Allergene.nome UNIQUE
ProdottoAllergene(prodotto_id, allergene_id) UNIQUE
ProdottoAlimentare(categoria_id, nome) UNIQUE
```


### 7.5 Vincoli sulle prenotazioni

- Ogni prenotazione deve essere associata a uno studente.
- Ogni prenotazione deve essere associata a un lotto esistente.
- La quantità prenotata deve essere maggiore di zero.
- La quantità prenotata non può superare la quantità disponibile del lotto.
- La quantità massima prenotabile per singola operazione è 99.
- Uno studente non può prenotare un lotto scaduto.
- Uno studente non può prenotare un lotto annullato.
- Uno studente non può prenotare un lotto chiuso.
- Una prenotazione ritirata o non ritirata non può essere annullata.
- Quando viene creata una prenotazione attiva, la quantità disponibile del lotto diminuisce.
- Quando una prenotazione attiva viene annullata, la quantità viene restituita al lotto.
- Se una prenotazione attiva supera la fascia oraria senza conferma, viene considerata `non_ritirata`.

Esempio:

```text
quantita_iniziale = 8
quantita_disponibile = 8

prenotazione Mario Rossi = 1
nuova quantita_disponibile = 7

altra prenotazione Mario Rossi = 2
nuova quantita_disponibile = 5
```

Questa operazione viene gestita in modo atomico, perché riguarda sia la creazione della prenotazione sia l'aggiornamento del lotto.

Stati possibili della prenotazione:

- `attiva`
- `annullata`
- `ritirata`
- `non_ritirata`
- `scaduta`

### 7.6 Vincoli sui ritiri

- Ogni ritiro deve riferirsi a una prenotazione.
- Una prenotazione può avere al massimo un ritiro.
- Ogni ritiro completato deve essere confermato da un operatore mensa.
- Il ritiro può essere confermato solo se la prenotazione è attiva.
- Il ritiro può essere confermato solo durante la fascia oraria prevista.
- Dopo il ritiro, la prenotazione passa allo stato `ritirata` se l'esito è `consegnato`.
- L'operatore può confermare solo ritiri relativi alla propria mensa.
- Il mancato ritiro viene gestito automaticamente quando la fascia oraria scade senza conferma.

Esiti possibili del ritiro:

- `consegnato`
- `non_consegnato`
- `annullato`

Nel flusso principale l'operatore usa direttamente l'azione `Segna ritirata`; il non ritiro deriva automaticamente dalla scadenza della fascia oraria.

### 7.7 Vincoli sulle recensioni

- Una recensione deve essere scritta da uno studente.
- Una recensione deve riferirsi a una mensa.
- Una recensione deve essere collegata a una prenotazione.
- Lo studente può recensire una mensa solo dopo un ritiro completato.
- Il voto è obbligatorio.
- Il voto deve essere compreso tra 1 e 5.
- Il voto viene selezionato tramite scelta vincolata, non tramite numero libero.
- Il commento è opzionale.
- Uno studente non può recensire due volte la stessa prenotazione.
- La recensione deve riguardare la mensa associata al lotto prenotato.

Esempio concreto:

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

## 8. Stati del dominio

### 8.1 Stati del LottoInvenduto

| Stato | Significato |
|---|---|
| `disponibile` | Il lotto è visibile agli studenti e può essere prenotato. |
| `esaurito` | La quantità disponibile è arrivata a zero. |
| `chiuso` | L'operatore ha chiuso manualmente il lotto. |
| `scaduto` | La data di ritiro o la fascia utile sono superate. |
| `annullato` | Il lotto è stato annullato per errore o problema operativo. |

### 8.2 Stati della Prenotazione

| Stato | Significato |
|---|---|
| `attiva` | La prenotazione è valida ma non ancora conclusa. |
| `annullata` | La prenotazione è stata annullata dallo studente. |
| `ritirata` | Lo studente ha ritirato il prodotto e l'operatore ha confermato il ritiro. |
| `non_ritirata` | La fascia di ritiro è terminata senza conferma del ritiro. |
| `scaduta` | Stato utilizzabile per indicare una prenotazione non più valida temporalmente. |

### 8.3 Stati interfaccia della Prenotazione

Gli stati interfaccia non sostituiscono gli stati del dominio, ma servono a comunicare meglio la situazione all'utente.

| Stato visualizzato | Significato |
|---|---|
| `Ritiro programmato` | Il ritiro è futuro. |
| `Pronta da ritirare` | Per lo studente: siamo dentro la fascia oraria di ritiro. |
| `In attesa di ritiro` | Per l'operatore: siamo dentro la fascia oraria e lo studente può presentarsi. |
| `Ritirata` | La prenotazione è stata conclusa positivamente. |
| `Non ritirata` | La prenotazione non è stata ritirata entro la fascia prevista. |
| `Annullata` | La prenotazione è stata annullata. |

Graficamente, gli stati sono distinti anche per peso visivo:

- `Ritiro programmato`: badge blu chiaro;
- `Pronta da ritirare` / `In attesa di ritiro`: badge verde chiaro;
- `Ritirata`: badge verde pieno;
- `Non ritirata`: badge rosso;
- `Annullata`: badge chiaro con bordo.

### 8.4 Stati della Segnalazione

| Stato | Significato |
|---|---|
| `aperta` | La segnalazione è stata creata ma non ancora gestita. |
| `in_carico` | Un amministratore ha preso in carico la segnalazione. |
| `risolta` | Il problema è stato gestito positivamente. |
| `respinta` | La segnalazione è stata valutata non fondata. |
| `chiusa` | La segnalazione è conclusa definitivamente. |

---

## 9. Scelte progettuali rilevanti

### 9.1 LottoInvenduto come entità centrale

La scelta più importante del progetto è modellare il `LottoInvenduto` come entità autonoma.

Il lotto non coincide con il prodotto alimentare.

```text
ProdottoAlimentare = Pasta al pomodoro
LottoInvenduto = 8 porzioni di Pasta al pomodoro disponibili oggi alla Mensa Centrale dalle 17:00 alle 18:00
```

Questa separazione è fondamentale perché lo stesso prodotto può essere presente in molti lotti diversi, in giorni diversi, in mense diverse e con quantità diverse.

Senza questa distinzione, il sistema sarebbe una semplice lista di pasti. Con questa distinzione, invece, diventa un sistema informativo capace di gestire disponibilità concrete, temporanee e tracciabili.

### 9.2 Codice unico del lotto

Il sistema usa un solo codice visibile:

```text
L-0001
```

Questo codice identifica il lotto.

Non vengono usati codici separati per prenotazione, ritiro o pubblicazione. La scelta evita confusione nell'interfaccia e mantiene una corrispondenza universale:

```text
L-0001 = stesso lotto in tutte le pagine
```

Lo stesso codice compare in:

- lotti pubblicati;
- ritiri da confermare;
- storico ritiri;
- prenotazioni dello studente;
- dashboard operatore.

Il prefisso `L` indica il lotto e il numero deriva dall'identificativo del record.

### 9.3 Separazione tra ProdottoAlimentare e LottoInvenduto

`ProdottoAlimentare` descrive il tipo di alimento.

`LottoInvenduto` descrive una disponibilità concreta e temporanea.

Questa scelta permette di evitare duplicazioni. Senza questa separazione, ogni volta che viene pubblicato un lotto bisognerebbe reinserire anche tutte le informazioni del prodotto: nome, descrizione, categoria, allergeni, caratteristiche vegetariane o vegane.

Separando le due entità, il prodotto viene registrato una sola volta e può essere riutilizzato in più lotti.

### 9.4 Gestione molti-a-molti degli allergeni

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

### 9.5 Quantità disponibile salvata nel lotto

Il campo `quantita_disponibile` viene salvato direttamente nel lotto.

Questa è una ridondanza controllata, perché teoricamente la quantità disponibile potrebbe essere calcolata così:

```text
quantita_disponibile = quantita_iniziale - somma(prenotazioni attive/ritirate/non_ritirate)
```

Tuttavia, per semplicità implementativa e chiarezza applicativa, viene mantenuto un campo dedicato.

Questa scelta richiede un vincolo applicativo: quando si crea o annulla una prenotazione, `quantita_disponibile` deve essere aggiornata correttamente.

Per evitare inconsistenze, l'aggiornamento viene gestito in transazione atomica, cioè come un'unica operazione indivisibile: la creazione della prenotazione e la riduzione della quantità disponibile devono riuscire entrambe. Se una delle due operazioni fallisce, anche l'altra viene annullata, evitando dati incoerenti.

### 9.6 Disponibilità e non ritirati

Una prenotazione non ritirata non restituisce automaticamente la quantità al lotto.

Questa scelta è realistica: se lo studente non si presenta entro la fascia oraria, la porzione potrebbe non essere più recuperabile, potrebbe essere scaduta o gestita diversamente dalla mensa.

Quindi:

```text
ritirata + non_ritirata = quantità non più disponibile
```

Esempio:

```text
quantità iniziale = 8
ritirata = 1
non_ritirata = 2

quantità disponibile = 5
```

Nella pagina dei lotti pubblicati può quindi apparire:

```text
5/8 disponibili
```

e nello storico ritiri/prenotazioni si vedono le quantità che giustificano la differenza.

### 9.7 Nessuna gestione dei pagamenti online

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

### 9.8 Ritiro e conferma operatore

Nel modello implementativo è presente il concetto di ritiro confermato dall'operatore.

La conferma del ritiro viene semplificata nell'interfaccia: l'operatore usa direttamente l'azione `Segna ritirata`.

Il non ritiro non viene gestito manualmente dall'operatore: viene determinato automaticamente quando la fascia oraria termina senza ritiro.

Questa scelta rende più chiaro il flusso operativo:

```text
ritiro effettivo -> operatore segna ritirata
mancato ritiro -> sistema segna non_ritirata automaticamente
annullamento -> azione dello studente prima del ritiro
```

### 9.9 Recensione vincolata al ritiro

La recensione può essere lasciata solo dopo un ritiro completato.

Questa scelta evita recensioni non motivate da un'esperienza reale. Uno studente può valutare una mensa solo se ha effettivamente prenotato e ritirato un lotto presso quella mensa.

Il voto è obbligatorio e deve essere compreso tra 1 e 5. Il commento è opzionale.

### 9.10 Segnalazioni collegate alla prenotazione

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

### 9.11 Ruolo come attributo discriminante

La presenza dei tre ruoli rende il sistema più realistico:

- lo studente non deve poter pubblicare lotti;
- l'operatore non deve poter gestire segnalazioni amministrative di sistema;
- l'amministratore non partecipa direttamente al processo di prenotazione e ritiro, ma supervisiona il sistema.

Nel modello concettuale scelto, il ruolo viene trattato come attributo discriminante. Non è un semplice campo descrittivo: determina quali relazioni l'utente può avere nel sistema.

Questa separazione permette di dimostrare competenze non solo nella progettazione del database, ma anche nella gestione dei permessi applicativi.

### 9.12 Dashboard e statistiche come valore informativo

La dashboard non è solo un elemento grafico, ma rappresenta una parte importante del sistema informativo.

Sono previste dashboard diverse per studenti, operatori e amministratori.

La home pubblica, senza accesso, mostra solo dati pubblici:

- lotti disponibili;
- porzioni disponibili;
- mense disponibili.

Non mostra dati personali o già associati a prenotazioni specifiche.

L'area operatore, invece, mostra dati operativi della propria mensa:

- lotti disponibili;
- porzioni disponibili;
- ritiri da confermare;
- ritiri confermati;
- lotti pubblicati di recente.

Questa separazione evita che la home pubblica mostri dati legati a specifici utenti, come le porzioni già ritirate da uno studente.

---

## 10. Query SQL significative

### 10.1 Ricerca dei lotti disponibili per mensa

```sql
SELECT l.id, p.nome, l.quantita_disponibile, l.ora_inizio_ritiro, l.ora_fine_ritiro
FROM LottoInvenduto l
JOIN ProdottoAlimentare p ON l.prodotto_id = p.id
JOIN Mensa m ON l.mensa_id = m.id
WHERE m.nome = 'Mensa Centrale'
AND l.stato = 'disponibile'
AND l.quantita_disponibile > 0;
```

### 10.2 Ricerca dei lotti che non contengono un certo allergene

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

### 10.3 Storico prenotazioni di uno studente

```sql
SELECT pr.id, p.nome, m.nome AS mensa, pr.quantita, pr.stato, pr.data_prenotazione
FROM Prenotazione pr
JOIN LottoInvenduto l ON pr.lotto_id = l.id
JOIN ProdottoAlimentare p ON l.prodotto_id = p.id
JOIN Mensa m ON l.mensa_id = m.id
WHERE pr.studente_id = 1
ORDER BY pr.data_prenotazione DESC;
```

### 10.4 Prenotazioni attive da ritirare per una mensa

```sql
SELECT pr.id, u.first_name, u.last_name, p.nome, pr.quantita, l.data_scadenza,
       l.ora_inizio_ritiro, l.ora_fine_ritiro
FROM Prenotazione pr
JOIN Studente s ON pr.studente_id = s.id
JOIN Utente u ON s.utente_id = u.id
JOIN LottoInvenduto l ON pr.lotto_id = l.id
JOIN ProdottoAlimentare p ON l.prodotto_id = p.id
WHERE l.mensa_id = 1
AND pr.stato = 'attiva'
ORDER BY l.data_scadenza, l.ora_inizio_ritiro;
```

### 10.5 Porzioni ritirate per mensa

```sql
SELECT m.nome, SUM(pr.quantita) AS porzioni_ritirate
FROM Ritiro r
JOIN Prenotazione pr ON r.prenotazione_id = pr.id
JOIN LottoInvenduto l ON pr.lotto_id = l.id
JOIN Mensa m ON l.mensa_id = m.id
WHERE pr.stato = 'ritirata'
GROUP BY m.nome;
```

### 10.6 Media recensioni per mensa

```sql
SELECT m.nome, AVG(rm.voto) AS voto_medio
FROM RecensioneMensa rm
JOIN Mensa m ON rm.mensa_id = m.id
GROUP BY m.nome;
```

### 10.7 Segnalazioni aperte o in carico

```sql
SELECT s.id, s.titolo, s.stato, s.data_apertura
FROM Segnalazione s
WHERE s.stato IN ('aperta', 'in_carico')
ORDER BY s.data_apertura ASC;
```

### 10.8 Lotti più richiesti

```sql
SELECT p.nome, COUNT(pr.id) AS numero_prenotazioni
FROM Prenotazione pr
JOIN LottoInvenduto l ON pr.lotto_id = l.id
JOIN ProdottoAlimentare p ON l.prodotto_id = p.id
GROUP BY p.nome
ORDER BY numero_prenotazioni DESC;
```

### 10.9 Quantità non recuperata stimata

```sql
SELECT m.nome, SUM(pr.quantita) AS quantita_non_ritirata
FROM Prenotazione pr
JOIN LottoInvenduto l ON pr.lotto_id = l.id
JOIN Mensa m ON l.mensa_id = m.id
WHERE pr.stato = 'non_ritirata'
GROUP BY m.nome;
```

### 10.10 Giustificazione quantità disponibile di un lotto

```sql
SELECT
    l.id,
    l.quantita_iniziale,
    l.quantita_disponibile,
    SUM(CASE WHEN pr.stato = 'ritirata' THEN pr.quantita ELSE 0 END) AS quantita_ritirata,
    SUM(CASE WHEN pr.stato = 'non_ritirata' THEN pr.quantita ELSE 0 END) AS quantita_non_ritirata,
    SUM(CASE WHEN pr.stato = 'attiva' THEN pr.quantita ELSE 0 END) AS quantita_da_ritirare
FROM LottoInvenduto l
LEFT JOIN Prenotazione pr ON pr.lotto_id = l.id
WHERE l.id = 1
GROUP BY l.id, l.quantita_iniziale, l.quantita_disponibile;
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
│   └── site.css
│
├── fixtures/                   # dati iniziali di esempio
│   └── initial_data.json
│
├── docs/                       # documentazione tecnica
│   ├── relazione.md
│   ├── alternative_generalizzazione.md
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

## 12. Organizzazione delle pagine

### 12.1 Area pubblica

- Home page
- Catalogo lotti disponibili
- Dettaglio lotto
- Recensioni mense
- Login
- Registrazione

La home pubblica mostra solo informazioni generali:

- lotti disponibili;
- porzioni disponibili;
- mense disponibili.

Non mostra dati personali o collegati a specifici studenti.

### 12.2 Area studente

- Dashboard studente
- Catalogo lotti
- Dettaglio lotto
- Prenota lotto
- Le mie prenotazioni
- Annulla prenotazione attiva
- Le mie recensioni
- Dettaglio recensione
- Apri segnalazione

Gli stati mostrati allo studente distinguono tra:

- `Ritiro programmato`, se la fascia è futura;
- `Pronta da ritirare`, se siamo dentro la fascia oraria;
- `Ritirata`, se l'operatore ha confermato il ritiro;
- `Non ritirata`, se la fascia è scaduta senza conferma;
- `Annullata`, se lo studente ha annullato.

### 12.3 Area operatore mensa

- Home operatore come dashboard operativa
- Pubblica lotto
- Lotti pubblicati
- Modifica lotto
- Chiudi lotto
- Ritiri da confermare
- Segna ritirata
- Storico ritiri
- Recensioni mense

L'operatore non visualizza la stessa home dello studente. Quando accede, vede una dashboard operativa della propria mensa.

La voce principale è `Pubblica lotto`, perché l'operatore pubblica disponibilità, non effettua prenotazioni.

### 12.4 Area amministratore

- Dashboard amministratore
- Gestione mense
- Gestione categorie
- Gestione prodotti
- Gestione allergeni
- Gestione segnalazioni
- Statistiche recupero alimentare

### 12.5 Area admin Django

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

## 13. Bonus sicurezza

### 13.1 Simulazione SQL injection

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

### 13.2 Simulazione brute-force

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

### 13.3 Protezioni applicative usate nel progetto

- Uso dell'ORM Django invece di query SQL concatenate manualmente.
- Uso di `transaction.atomic()` per operazioni critiche su prenotazioni e quantità.
- Uso di `select_for_update()` per ridurre il rischio di race condition nella prenotazione dei lotti.
- Controlli sui ruoli tramite funzioni di permesso.
- Vincoli nei modelli tramite `clean()` e validatori Django.
- Validazione lato form per quantità, date, voto recensione e dati obbligatori.
- Protezione CSRF nativa nei form Django.
- Separazione tra pagine pubbliche e aree riservate per ruolo.

---

## 14. Considerazioni finali

**UniFood Rescue** rappresenta un sistema completo e significativa con gli obiettivi:

- utenti con ruoli differenti;
- una generalizzazione/specializzazione coerente;
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
- monitoraggio delle quantità recuperate;
- distinzione tra dati pubblici, dati studente e dati operatore.

Il cuore del sistema è il seguente flusso:

- `Utente` con ruolo discriminante;
- `ProdottoAlimentare` <-> `Allergene`;
- `Mensa` -> `LottoInvenduto`;
- `LottoInvenduto` -> `Prenotazione`;
- `Prenotazione` -> `Ritiro`;
- `Prenotazione` -> `Segnalazione`;
- `Mensa` -> `RecensioneMensa`.

Inoltre, l'introduzione di prenotazioni, ritiri, recensioni e segnalazioni permette di modellare un ciclo di vita completo del dato: dalla pubblicazione del lotto fino alla sua effettiva consegna o alla gestione di eventuali problemi.

La scelta sulla generalizzazione rafforza il progetto: il ruolo è un attributo fondamentale, perché determina il comportamento dell'utente nel sistema. Tuttavia, poiché studenti, operatori e amministratori condividono le stesse credenziali e lo stesso meccanismo di accesso, si è preferito mantenere una logica centrata sull'entità `Utente`, usando `ruolo` come attributo discriminante.
