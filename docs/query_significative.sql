-- Lotti disponibili per mensa
SELECT l.id, p.nome, l.quantita_disponibile
FROM mensa_lottoinvenduto l
JOIN mensa_prodottoalimentare p ON l.prodotto_id = p.id
JOIN mensa_mensa m ON l.mensa_id = m.id
WHERE m.nome = 'Mensa Centrale'
  AND l.stato = 'disponibile'
  AND l.quantita_disponibile > 0;

-- Prodotti senza lattosio
SELECT DISTINCT l.id, p.nome, m.nome AS mensa
FROM mensa_lottoinvenduto l
JOIN mensa_prodottoalimentare p ON l.prodotto_id = p.id
JOIN mensa_mensa m ON l.mensa_id = m.id
WHERE p.id NOT IN (
  SELECT pa.prodotto_id
  FROM mensa_prodottoallergene pa
  JOIN mensa_allergene a ON pa.allergene_id = a.id
  WHERE lower(a.nome) = 'lattosio'
);

-- Storico prenotazioni studente
SELECT pr.id, p.nome, m.nome, pr.quantita, pr.stato
FROM mensa_prenotazione pr
JOIN mensa_lottoinvenduto l ON pr.lotto_id = l.id
JOIN mensa_prodottoalimentare p ON l.prodotto_id = p.id
JOIN mensa_mensa m ON l.mensa_id = m.id
WHERE pr.studente_id = 1
ORDER BY pr.data_prenotazione DESC;

-- Porzioni recuperate per mensa
SELECT m.nome, SUM(pr.quantita) AS porzioni_ritirate
FROM mensa_ritiro r
JOIN mensa_prenotazione pr ON r.prenotazione_id = pr.id
JOIN mensa_lottoinvenduto l ON pr.lotto_id = l.id
JOIN mensa_mensa m ON l.mensa_id = m.id
WHERE pr.stato = 'ritirata'
GROUP BY m.nome;
