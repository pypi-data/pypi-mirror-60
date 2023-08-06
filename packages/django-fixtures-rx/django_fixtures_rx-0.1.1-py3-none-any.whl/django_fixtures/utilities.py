import inspect
import os
from typing import TYPE_CHECKING, List

from django.core.management import call_command
from django.db import connections

from . import exceptions
from .helpers import *

if TYPE_CHECKING:
    from .fixtures import BaseFixture


def cleanup_database():
    database_name = get_database_name()
    database_path = get_database_path(database_name)

    connections.close_all()

    if database_name in connections._databases:
        connections._databases.pop(database_name)

    if os.path.isfile(database_path):
        os.remove(database_path)


def prepare_database():
    cleanup_database()
    database_name = get_database_name()

    connections._databases[database_name] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': get_database_path(database_name),
    }


def lookup_fixtures(app_label: str = None) -> List['BaseFixture']:
    apps_labels, fixtures = [app_label] if app_label else get_apps_labels(), []

    for app_label in apps_labels:
        try:
            fixtures_module = get_fixtures_module(app_label)
        except (LookupError, exceptions.FixturesNotFound):
            continue

        for name, fixture_class in inspect.getmembers(fixtures_module, is_fixture_class):
            if not inspect.isabstract(fixture_class):
                fixtures.append(fixture_class(app_label))

    return fixtures


def get_fixtures(*accessors: str) -> List['BaseFixture']:
    fixtures = [] if accessors else lookup_fixtures()

    for accessor in accessors:
        if '.' not in accessor:
            if not len(fixtures_lookup := lookup_fixtures(accessor)):
                raise exceptions.FixturesNotFound(accessor)

            fixtures += fixtures_lookup
        else:
            app_label, fixture_name = accessor.split('.', 1)

            try:
                fixtures_module = get_fixtures_module(app_label)
            except (LookupError, exceptions.FixturesNotFound):
                raise exceptions.FixtureNotFound(accessor)

            if hasattr(fixtures_module, fixture_name):
                fixtures.append(getattr(fixtures_module, fixture_name)(app_label))
            else:
                raise exceptions.FixtureNotFound(accessor)

    return fixtures


def create_fixtures(*accessors: str):
    prepare_database()

    try:
        for fixture in get_fixtures(*accessors):
            call_command('migratefixtures', no_input=True, verbosity=0), fixture.create_fixture()
            call_command('flush', database=get_database_name(), verbosity=0, interactive=False)
    except Exception as exception:
        raise exception
    finally:
        cleanup_database()


def load_fixtures(*accessors: str) -> dict:
    return {f'{f.app_label}.{f.name}': d for f in get_fixtures(*accessors) if (d := f.load())}
