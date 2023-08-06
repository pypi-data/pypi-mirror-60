from django.core.management import call_command
from django.test import TestCase

from .helpers import get_database_name
from .utilities import load_fixtures, prepare_database, cleanup_database


class FixturesTestCase(TestCase):
    fixtures_data, database = None, get_database_name()

    @classmethod
    def setUpClass(cls):
        cls.databases = [*cls.databases, cls.database]
        prepare_database(), call_command('migratefixtures', no_input=True, verbosity=0)

        if cls.fixtures is not None:
            cls.fixtures_data = load_fixtures(*cls.fixtures)

        cls.fixtures = []
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cleanup_database(), super().tearDownClass()
