# Bonus sicurezza

## SQL injection

Codice vulnerabile da evitare:

```python
query = "SELECT * FROM ProdottoAlimentare WHERE nome LIKE '%" + ricerca + "%'"
```

Nel progetto si usa l'ORM:

```python
ProdottoAlimentare.objects.filter(nome__icontains=ricerca)
```

L'input viene parametrizzato e non concatenato manualmente.

## Brute force

Misure presenti o consigliate:

- password hashate da Django;
- validatori password;
- CSRF nei form;
- session cookie HTTP-only;
- possibilità di aggiungere rate limiting o `django-axes`;
- logging dei tentativi falliti.

## Integrità

Le prenotazioni usano `transaction.atomic()` e `select_for_update()` per evitare overbooking dei lotti.
