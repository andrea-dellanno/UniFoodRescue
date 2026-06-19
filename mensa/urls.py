from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('lotti/', views.catalogo_lotti, name='catalogo_lotti'),
    path('lotti/<int:pk>/', views.dettaglio_lotto, name='dettaglio_lotto'),
    path('registrazione/', views.registrazione, name='registrazione'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('studente/', views.dashboard_studente, name='dashboard_studente'),
    path('studente/lotti/<int:pk>/prenota/', views.prenota_lotto, name='prenota_lotto'),
    path('studente/prenotazioni/', views.mie_prenotazioni, name='mie_prenotazioni'),
    path('studente/prenotazioni/<int:pk>/annulla/', views.annulla_prenotazione, name='annulla_prenotazione'),
    path('studente/prenotazioni/<int:prenotazione_id>/recensione/', views.crea_recensione, name='crea_recensione'),
    path('studente/prenotazioni/<int:prenotazione_id>/segnalazione/', views.apri_segnalazione, name='apri_segnalazione'),

    path('operatore/', views.dashboard_operatore, name='dashboard_operatore'),
    path('operatore/lotti/', views.gestisci_lotti, name='gestisci_lotti'),
    path('operatore/lotti/nuovo/', views.crea_lotto, name='crea_lotto'),
    path('operatore/lotti/<int:pk>/modifica/', views.modifica_lotto, name='modifica_lotto'),
    path('operatore/lotti/<int:pk>/chiudi/', views.chiudi_lotto, name='chiudi_lotto'),
    path('operatore/ritiri/', views.prenotazioni_da_ritirare, name='prenotazioni_da_ritirare'),
    path('operatore/ritiri/<int:prenotazione_id>/conferma/', views.conferma_ritiro, name='conferma_ritiro'),
    path('operatore/storico-ritiri/', views.storico_ritiri_operatore, name='storico_ritiri_operatore'),

    path('amministrazione/', views.dashboard_amministratore, name='dashboard_amministratore'),
    path('amministrazione/mense/', views.MensaList.as_view(), name='admin_mensa_list'),
    path('amministrazione/mense/nuova/', views.MensaCreate.as_view(), name='admin_mensa_create'),
    path('amministrazione/mense/<int:pk>/modifica/', views.MensaUpdate.as_view(), name='admin_mensa_update'),
    path('amministrazione/categorie/', views.CategoriaList.as_view(), name='admin_categoria_list'),
    path('amministrazione/categorie/nuova/', views.CategoriaCreate.as_view(), name='admin_categoria_create'),
    path('amministrazione/categorie/<int:pk>/modifica/', views.CategoriaUpdate.as_view(), name='admin_categoria_update'),
    path('amministrazione/allergeni/', views.AllergeneList.as_view(), name='admin_allergene_list'),
    path('amministrazione/allergeni/nuovo/', views.AllergeneCreate.as_view(), name='admin_allergene_create'),
    path('amministrazione/allergeni/<int:pk>/modifica/', views.AllergeneUpdate.as_view(), name='admin_allergene_update'),
    path('amministrazione/prodotti/', views.ProdottoList.as_view(), name='admin_prodotto_list'),
    path('amministrazione/prodotti/nuovo/', views.ProdottoCreate.as_view(), name='admin_prodotto_create'),
    path('amministrazione/prodotti/<int:pk>/modifica/', views.ProdottoUpdate.as_view(), name='admin_prodotto_update'),
    path('amministrazione/segnalazioni/', views.gestione_segnalazioni, name='gestione_segnalazioni'),
    path('amministrazione/segnalazioni/<int:pk>/', views.gestisci_segnalazione, name='gestisci_segnalazione'),
]
