from django.core.management.base import BaseCommand
from django.utils import timezone
from mensa.models import LottoInvenduto, StatiLotto

class Command(BaseCommand):
    help = 'Marca come scaduti i lotti disponibili oltre scadenza.'

    def handle(self, *args, **options):
        n = LottoInvenduto.objects.filter(stato=StatiLotto.DISPONIBILE, data_scadenza__lt=timezone.localdate()).update(stato=StatiLotto.SCADUTO)
        self.stdout.write(self.style.SUCCESS(f'Lotti aggiornati: {n}'))
