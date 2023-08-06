from django.core.management.commands.migrate import Command as MigrateCommand

from django_fixtures.helpers import get_database_name
from django_fixtures.utilities import prepare_database


class Command(MigrateCommand):
    help = 'Used to migrate temp fixtures database.'

    def __init__(self, *args, **kwargs):
        prepare_database()
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        return super().handle(*args, **{**options, 'database': get_database_name()})
