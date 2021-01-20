def _elements(thing):
    try:
        yield from thing.__dict__.values()
        return
    except AttributeError:
        pass
    try:
        yield from thing.values()
        return
    except AttributeError:
        pass
    try:
        yield from thing
        return
    except TypeError:
        pass
    yield thing
    return


def elements(thing):
    for x in _elements(thing):
        if isinstance(x, (dict, list)):
            yield tuple(elements(x))
        else:
            yield x


class AutoEqHash:

    def __eq__(self, other):
        return type(self) == type(other) and self.__dict__ == other.__dict__

    def __hash__(self):
        # noinspection PyTypeChecker
        return hash(tuple(elements(self)))


class AutoRepr:

    def __repr__(self):
        return f"{type(self).__name__}({self.__dict__})"
