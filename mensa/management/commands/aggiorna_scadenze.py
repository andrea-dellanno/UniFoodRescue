from django.core.management.base import BaseCommand
from mensa.models import aggiorna_stati_automatici


class Command(BaseCommand):
    help = 'Aggiorna lotti scaduti, lotti esauriti e prenotazioni non ritirate.'

    def handle(self, *args, **options):
        risultati = aggiorna_stati_automatici()

        self.stdout.write(
            self.style.SUCCESS(
                'Aggiornamento completato: '
                f"{risultati['lotti_scaduti']} lotti scaduti, "
                f"{risultati['lotti_esauriti']} lotti esauriti, "
                f"{risultati['prenotazioni_non_ritirate']} prenotazioni non ritirate."
            )
        )