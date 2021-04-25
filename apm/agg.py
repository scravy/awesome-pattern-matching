from typing import Union

from apm.core import Aggregation


class Histogram(Aggregation[dict]):
    def new(self) -> dict:
        return dict()

    def _add(self, aggregate: dict, value) -> dict:
        if value not in aggregate:
            aggregate[value] = 0
        aggregate[value] += 1
        return aggregate


class Set(Aggregation[set]):
    def new(self) -> set:
        return set()

    def _add(self, aggregate: set, value) -> set:
        aggregate.add(value)
        return aggregate


class List(Aggregation[list]):
    def new(self) -> list:
        return list()

    def _add(self, aggregate: list, value) -> list:
        aggregate.append(value)
        return aggregate


class Sum(Aggregation[Union[int, float]]):
    def new(self) -> Union[int, float]:
        return 0

    def _add(self, aggregate: Union[int, float], value) -> Union[int, float]:
        try:
            return aggregate + int(value)
        except ValueError:
            return aggregate + float(value)


class Count(Aggregation[int]):
    def new(self) -> int:
        return 0

    def _add(self, aggregate: int, value) -> int:
        return aggregate + 1
