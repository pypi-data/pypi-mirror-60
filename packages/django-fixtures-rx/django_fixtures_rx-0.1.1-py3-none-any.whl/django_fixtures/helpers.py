import importlib.util
import inspect
import os
from types import ModuleType
from typing import List

from django.apps import apps
from django.conf import settings

from .exceptions import FixturesNotFound

__all__ = [
    'get_database_name', 'get_database_path', 'snake_case',
    'get_apps_labels', 'get_app_path', 'get_fixtures_path',
    'get_fixture_filepath', 'get_fixtures_module', 'is_fixture_class'
]


def get_database_name() -> str:
    if hasattr(settings, 'FIXTURES_DATABASE_NAME'):
        return str(settings.FIXTURES_DATABASE_NAME)
    else:
        return '__tempfixtures__'


def get_database_path(database_name: str = None) -> str:
    database_name = database_name if database_name else get_database_name()
    return os.path.join(os.path.dirname(__file__), f'{database_name}.sqlite3')


def snake_case(camel_name: str, divider: str = '-') -> str:
    snake_case_name = ''

    for index, symbol in enumerate(camel_name):
        if symbol.isupper() and index not in [0, len(camel_name) - 1] and not camel_name[index + 1].isupper():
            snake_case_name += divider

        snake_case_name += symbol.lower()

    return snake_case_name


def get_apps_labels() -> List[str]:
    return [app.label for app in apps.get_app_configs()]


def get_app_path(app_label: str) -> str:
    return apps.get_app_config(app_label).path


def get_fixtures_path(app_label: str):
    return os.path.join(get_app_path(app_label), 'fixtures')


def get_fixture_filepath(app_label: str, name: str) -> str:
    fixtures_path = get_fixtures_path(app_label)

    if not os.path.isdir(fixtures_path):
        os.mkdir(fixtures_path)

    return os.path.join(fixtures_path, f'{name}.json')


def get_fixtures_module(app_label: str) -> ModuleType:
    try:
        fixtures_filepath = os.path.sep.join([get_app_path(app_label), 'fixtures.py'])
        spec = importlib.util.spec_from_file_location('__tempmodule__', fixtures_filepath)
        spec.loader.exec_module(module := importlib.util.module_from_spec(spec))
    except FileNotFoundError:
        raise FixturesNotFound(app_label)

    return module


def is_fixture_class(class_: type) -> bool:
    from .fixtures import BaseFixture
    return hasattr(class_, '__mro__') and BaseFixture in inspect.getmro(class_)
