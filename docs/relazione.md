# Relazione progettuale — UniFood Rescue

## Analisi del dominio

UniFood Rescue è un sistema informativo per il recupero delle eccedenze alimentari delle mense universitarie. Il focus non è vendere pasti o gestire consegne, ma tracciare lotti invenduti, quantità disponibili, allergeni, prenotazioni, ritiri, recensioni e segnalazioni.

## Modello concettuale

Entità principali:

- Utente
- Studente
- OperatoreMensa
- Amministratore
- Mensa
- CategoriaAlimento
- ProdottoAlimentare
- Allergene
- ProdottoAllergene
- LottoInvenduto
- Prenotazione
- Ritiro
- RecensioneMensa
- Segnalazione

Il lotto invenduto è l'entità centrale: rappresenta una disponibilità concreta giornaliera di un prodotto presso una mensa.

## Generalizzazione / specializzazione

Gerarchia:

```text
Utente
├── Studente
├── OperatoreMensa
└── Amministratore
```

La generalizzazione è totale e disgiunta: ogni utente deve avere un solo ruolo operativo.

Alternative valutate:

1. Tutto in `Utente`: semplice ma produce molti `NULL` e vincoli condizionali.
2. Solo tabelle figlie: elimina `NULL`, ma duplica username, email e password.
3. Tabella padre + tabelle figlie: migliore normalizzazione e compatibilità con Django.

Scelta: alternativa 3, implementata con `Utente(AbstractUser)` e profili 1:1.

## Modello logico

```text
Utente(id, username, password, first_name, last_name, email, ruolo)
Studente(id, utente_id UNIQUE FK, matricola UNIQUE, corso_studi, anno_corso, data_registrazione)
OperatoreMensa(id, utente_id UNIQUE FK, mensa_id FK, codice_operatore UNIQUE, mansione, data_assunzione)
Amministratore(id, utente_id UNIQUE FK, area_responsabilita)
Mensa(id, nome UNIQUE, edificio, indirizzo, orario_apertura, orario_chiusura, attiva)
CategoriaAlimento(id, nome UNIQUE, descrizione)
ProdottoAlimentare(id, categoria_id FK, nome, descrizione, vegetariano, vegano, attivo)
Allergene(id, nome UNIQUE, descrizione)
ProdottoAllergene(id, prodotto_id FK, allergene_id FK)
LottoInvenduto(id, mensa_id FK, prodotto_id FK, operatore_id FK, quantita_iniziale, quantita_disponibile, data_pubblicazione, data_scadenza, ora_inizio_ritiro, ora_fine_ritiro, prezzo_simbolico, stato, note)
Prenotazione(id, studente_id FK, lotto_id FK, quantita, stato, data_prenotazione)
Ritiro(id, prenotazione_id UNIQUE FK, operatore_id FK, data_ora_ritiro, esito, note)
RecensioneMensa(id, studente_id FK, mensa_id FK, prenotazione_id UNIQUE FK, voto, commento, data_inserimento)
Segnalazione(id, prenotazione_id FK, autore_id FK, amministratore_id FK NULL, titolo, descrizione, stato, esito, data_apertura, data_chiusura)
```

## Cardinalità

- Mensa 1:N OperatoreMensa.
- CategoriaAlimento 1:N ProdottoAlimentare.
- ProdottoAlimentare N:N Allergene tramite ProdottoAllergene.
- Mensa 1:N LottoInvenduto.
- ProdottoAlimentare 1:N LottoInvenduto.
- OperatoreMensa 1:N LottoInvenduto.
- Studente 1:N Prenotazione.
- LottoInvenduto 1:N Prenotazione.
- Prenotazione 1:0..1 Ritiro.
- OperatoreMensa 1:N Ritiro.
- Studente 1:N RecensioneMensa.
- Mensa 1:N RecensioneMensa.
- Prenotazione 1:N Segnalazione.
- Studente 1:N Segnalazione.
- Amministratore 0:N Segnalazione.

## Vincoli

- Quantità iniziale maggiore di zero.
- Quantità disponibile non negativa e non maggiore della quantità iniziale.
- Scadenza non precedente alla pubblicazione.
- Fine ritiro successiva all'inizio ritiro.
- Operatore vincolato alla propria mensa.
- Prenotazione consentita solo se il lotto è disponibile, non scaduto e con quantità sufficiente.
- Creazione prenotazione e decremento quantità in transazione.
- Annullamento prenotazione attiva e restituzione quantità in transazione.
- Ritiro confermabile solo dall'operatore della mensa.
- Recensione consentita solo dopo ritiro completato.
- Segnalazione aperta solo dallo studente titolare della prenotazione.
