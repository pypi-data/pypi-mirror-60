import abc
from typing import Any, Generator, List


class Output(object):

    @abc.abstractmethod
    def ingest(self, columns: List[str], rows: Generator[List[Any], None, None]) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError
