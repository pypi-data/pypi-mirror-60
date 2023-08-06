from argparse import ArgumentParser

from django.core.management.base import BaseCommand

from django_fixtures.utilities import create_fixtures


class Command(BaseCommand):
    help = 'Used to create a fixtures.'

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            'args', metavar='app_label[.FixtureName]', nargs='*',
            help='Create fixtures for the specified app_label or app_label.FixtureName.'
        )

    def handle(self, *accessors, **options):
        try:
            create_fixtures(*accessors)
        except Exception as exception:
            self.stderr.write(str(exception))
