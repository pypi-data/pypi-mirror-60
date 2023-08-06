import json
from abc import abstractmethod, ABCMeta, ABC
from typing import Any, List

from django.core.management import call_command

from .datasets import CommonDatasetMixin
from .helpers import *
from .utilities import load_fixtures

__all__ = [
    'BaseFixture', 'JSONFixture', 'ModelFixture'
]


class BaseFixture(CommonDatasetMixin, metaclass=ABCMeta):
    fixtures, database = None, get_database_name()

    def __init__(self, app_label: str):
        self.app_label, self.name = app_label, self.__class__.__name__
        self.filepath = get_fixture_filepath(app_label, snake_case(self.name))

    def save(self, fixture: List[dict]):
        with open(self.filepath, 'w+') as file:
            file.write(json.dumps(list(fixture)))

    def load(self) -> List[dict]:
        with open(self.filepath, 'r+') as file:
            return json.loads(file.read())

    @abstractmethod
    def process_dataset_entry(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    def generate_fixture(self) -> List[dict]:
        pass

    def create_fixture(self):
        if (initial_fixtures := self.fixtures) is not None:
            self.fixtures = load_fixtures(*self.fixtures)

        self.save(self.generate_fixture())
        self.fixtures = initial_fixtures


class JSONFixture(BaseFixture, ABC):
    def serialize_dataset_entry(self, entry: dict) -> dict:
        return entry

    def generate_fixture(self) -> List[dict]:
        for entry in self.dataset:
            args, kwargs = self.prepare_dataset_entry(entry)
            entry = self.process_dataset_entry(*args, **kwargs)

            yield self.serialize_dataset_entry(entry)


class ModelFixture(BaseFixture, ABC):
    models = None

    def save(self, *args):
        models_list = [f'{model._meta.app_label}.{model._meta.object_name}' for model in self.models]
        call_command('dumpdata', *models_list, verbosity=0, database=self.database, output=self.filepath)

    def load(self):
        call_command('loaddata', self.filepath, verbosity=0, database=self.database)

    def generate_fixture(self):
        for entry in self.dataset:
            args, kwargs = self.prepare_dataset_entry(entry)
            entry = self.process_dataset_entry(*args, **kwargs)

            entry.save(using=self.database)
