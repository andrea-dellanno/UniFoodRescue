-- ============================================================
-- UniFood Rescue
-- Query SQL significative
-- ============================================================


-- 1. Ricerca dei lotti disponibili per mensa
-- Mostra i lotti ancora prenotabili presso una determinata mensa.

SELECT
    l.id,
    p.nome AS prodotto,
    m.nome AS mensa,
    l.quantita_disponibile,
    l.ora_inizio_ritiro,
    l.ora_fine_ritiro
FROM mensa_lottoinvenduto l
JOIN mensa_prodottoalimentare p ON l.prodotto_id = p.id
JOIN mensa_mensa m ON l.mensa_id = m.id
WHERE m.nome = 'Mensa Centrale'
AND l.stato = 'disponibile'
AND l.quantita_disponibile > 0;


-- 2. Ricerca dei lotti che non contengono un certo allergene
-- Esempio: prodotti senza lattosio.

SELECT DISTINCT
    l.id,
    p.nome AS prodotto,
    m.nome AS mensa,
    l.quantita_disponibile
FROM mensa_lottoinvenduto l
JOIN mensa_prodottoalimentare p ON l.prodotto_id = p.id
JOIN mensa_mensa m ON l.mensa_id = m.id
WHERE l.stato = 'disponibile'
AND l.quantita_disponibile > 0
AND p.id NOT IN (
    SELECT pa.prodotto_id
    FROM mensa_prodottoallergene pa
    JOIN mensa_allergene a ON pa.allergene_id = a.id
    WHERE LOWER(a.nome) = 'lattosio'
);


-- 3. Storico prenotazioni di uno studente
-- Mostra tutte le prenotazioni effettuate da uno studente.

SELECT
    pr.id,
    u.first_name,
    u.last_name,
    p.nome AS prodotto,
    m.nome AS mensa,
    pr.quantita,
    pr.stato,
    pr.data_prenotazione
FROM mensa_prenotazione pr
JOIN mensa_studente s ON pr.studente_id = s.id
JOIN mensa_utente u ON s.utente_id = u.id
JOIN mensa_lottoinvenduto l ON pr.lotto_id = l.id
JOIN mensa_prodottoalimentare p ON l.prodotto_id = p.id
JOIN mensa_mensa m ON l.mensa_id = m.id
WHERE pr.studente_id = 1
ORDER BY pr.data_prenotazione DESC;


-- 4. Prenotazioni attive da ritirare per una mensa
-- Mostra le prenotazioni ancora attive relative ai lotti di una mensa.

SELECT
    pr.id,
    u.first_name,
    u.last_name,
    p.nome AS prodotto,
    pr.quantita,
    l.data_scadenza,
    l.ora_inizio_ritiro,
    l.ora_fine_ritiro
FROM mensa_prenotazione pr
JOIN mensa_studente s ON pr.studente_id = s.id
JOIN mensa_utente u ON s.utente_id = u.id
JOIN mensa_lottoinvenduto l ON pr.lotto_id = l.id
JOIN mensa_prodottoalimentare p ON l.prodotto_id = p.id
WHERE l.mensa_id = 1
AND pr.stato = 'attiva'
ORDER BY l.data_scadenza, l.ora_inizio_ritiro;


-- 5. Porzioni ritirate per mensa
-- Calcola il totale delle porzioni effettivamente ritirate per ogni mensa.

SELECT
    m.nome AS mensa,
    SUM(pr.quantita) AS porzioni_ritirate
FROM mensa_prenotazione pr
JOIN mensa_lottoinvenduto l ON pr.lotto_id = l.id
JOIN mensa_mensa m ON l.mensa_id = m.id
WHERE pr.stato = 'ritirata'
GROUP BY m.nome;


-- 6. Media recensioni per mensa
-- Calcola il voto medio ricevuto da ogni mensa.

SELECT
    m.nome AS mensa,
    AVG(r.voto) AS voto_medio
FROM mensa_recensionemensa r
JOIN mensa_mensa m ON r.mensa_id = m.id
GROUP BY m.nome;


-- 7. Segnalazioni aperte o in carico
-- Mostra le segnalazioni ancora da gestire o già prese in carico.

SELECT
    s.id,
    s.titolo,
    s.stato,
    s.data_apertura
FROM mensa_segnalazione s
WHERE s.stato IN ('aperta', 'in_carico')
ORDER BY s.data_apertura ASC;


-- 8. Lotti più richiesti
-- Mostra i prodotti più prenotati dagli studenti.

SELECT
    p.nome AS prodotto,
    COUNT(pr.id) AS numero_prenotazioni
FROM mensa_prenotazione pr
JOIN mensa_lottoinvenduto l ON pr.lotto_id = l.id
JOIN mensa_prodottoalimentare p ON l.prodotto_id = p.id
GROUP BY p.nome
ORDER BY numero_prenotazioni DESC;


-- 9. Quantità non recuperata stimata
-- Calcola le porzioni prenotate ma non ritirate, raggruppate per mensa.

SELECT
    m.nome AS mensa,
    SUM(pr.quantita) AS quantita_non_ritirata
FROM mensa_prenotazione pr
JOIN mensa_lottoinvenduto l ON pr.lotto_id = l.id
JOIN mensa_mensa m ON l.mensa_id = m.id
WHERE pr.stato = 'non_ritirata'
GROUP BY m.nome;


-- 10. Giustificazione della quantità disponibile di un lotto
-- Mostra come la quantità disponibile sia giustificata dalle prenotazioni collegate.

SELECT
    l.id,
    l.quantita_iniziale,
    l.quantita_disponibile,
    COALESCE(SUM(CASE WHEN pr.stato = 'ritirata' THEN pr.quantita ELSE 0 END), 0) AS quantita_ritirata,
    COALESCE(SUM(CASE WHEN pr.stato = 'non_ritirata' THEN pr.quantita ELSE 0 END), 0) AS quantita_non_ritirata,
    COALESCE(SUM(CASE WHEN pr.stato = 'attiva' THEN pr.quantita ELSE 0 END), 0) AS quantita_da_ritirare
FROM mensa_lottoinvenduto l
LEFT JOIN mensa_prenotazione pr ON pr.lotto_id = l.id
WHERE l.id = 1
GROUP BY l.id, l.quantita_iniziale, l.quantita_disponibile;


-- 11. Lotti pronti al ritiro nella fascia oraria corrente
-- Mostra i lotti disponibili oggi e ritirabili nell'orario corrente.

SELECT
    l.id,
    p.nome AS prodotto,
    m.nome AS mensa,
    l.quantita_disponibile,
    l.data_scadenza,
    l.ora_inizio_ritiro,
    l.ora_fine_ritiro,
    l.stato
FROM mensa_lottoinvenduto l
JOIN mensa_prodottoalimentare p ON l.prodotto_id = p.id
JOIN mensa_mensa m ON l.mensa_id = m.id
WHERE l.stato = 'disponibile'
AND l.quantita_disponibile > 0
AND l.data_scadenza = DATE('now')
AND TIME('now') BETWEEN l.ora_inizio_ritiro AND l.ora_fine_ritiro
ORDER BY l.ora_fine_ritiro ASC;


-- 12. Lotti disponibili ma mai prenotati
-- Individua i lotti ancora disponibili che non hanno ancora ricevuto prenotazioni.

SELECT
    l.id,
    p.nome AS prodotto,
    m.nome AS mensa,
    l.quantita_iniziale,
    l.quantita_disponibile,
    l.data_pubblicazione,
    l.stato
FROM mensa_lottoinvenduto l
JOIN mensa_prodottoalimentare p ON l.prodotto_id = p.id
JOIN mensa_mensa m ON l.mensa_id = m.id
LEFT JOIN mensa_prenotazione pr ON pr.lotto_id = l.id
WHERE pr.id IS NULL
AND l.stato = 'disponibile'
AND l.quantita_disponibile > 0
ORDER BY l.data_pubblicazione DESC;


-- 13. Studenti con più prenotazioni non ritirate
-- Mostra gli studenti che hanno accumulato almeno una prenotazione non ritirata.

SELECT
    u.id,
    u.first_name,
    u.last_name,
    u.email,
    COUNT(pr.id) AS numero_non_ritirate,
    SUM(pr.quantita) AS porzioni_non_ritirate
FROM mensa_prenotazione pr
JOIN mensa_studente s ON pr.studente_id = s.id
JOIN mensa_utente u ON s.utente_id = u.id
WHERE pr.stato = 'non_ritirata'
GROUP BY u.id, u.first_name, u.last_name, u.email
HAVING COUNT(pr.id) >= 1
ORDER BY numero_non_ritirate DESC, porzioni_non_ritirate DESC;


-- 14. Prodotti con elenco degli allergeni
-- Mostra ogni prodotto con gli allergeni associati, usando una aggregazione testuale.

SELECT
    p.id,
    p.nome AS prodotto,
    GROUP_CONCAT(a.nome, ', ') AS allergeni
FROM mensa_prodottoalimentare p
LEFT JOIN mensa_prodottoallergene pa ON pa.prodotto_id = p.id
LEFT JOIN mensa_allergene a ON pa.allergene_id = a.id
GROUP BY p.id, p.nome
ORDER BY p.nome ASC;


-- 15. Tasso di recupero per mensa
-- Calcola, per ogni mensa, quante porzioni prenotate sono state effettivamente ritirate.

SELECT
    m.nome AS mensa,
    SUM(CASE WHEN pr.stato = 'ritirata' THEN pr.quantita ELSE 0 END) AS porzioni_ritirate,
    SUM(CASE WHEN pr.stato IN ('ritirata', 'non_ritirata') THEN pr.quantita ELSE 0 END) AS porzioni_concluse,
    ROUND(
        100.0 * SUM(CASE WHEN pr.stato = 'ritirata' THEN pr.quantita ELSE 0 END)
        / NULLIF(SUM(CASE WHEN pr.stato IN ('ritirata', 'non_ritirata') THEN pr.quantita ELSE 0 END), 0),
        2
    ) AS percentuale_recupero
FROM mensa_prenotazione pr
JOIN mensa_lottoinvenduto l ON pr.lotto_id = l.id
JOIN mensa_mensa m ON l.mensa_id = m.id
WHERE pr.stato IN ('ritirata', 'non_ritirata')
GROUP BY m.nome
ORDER BY percentuale_recupero DESC;
