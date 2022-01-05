#!/usr/bin/python3

from __future__ import annotations

import os
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from timeit import timeit
from typing import Optional, Type, List, TypeVar, Generic, get_args

from apm import *
from apm.no_value import NoValue

ROUNDS = int(os.environ.get('ROUNDS', '1000'))

DETAILED = bool(os.environ.get('DETAILED', '').lower() in ('yes', 'true', 'on', '1', 'enabled'))


@dataclass
class Point:
    x: int
    y: int


class Button(Enum):
    LEFT = auto()
    MIDDLE = auto()
    RIGHT = auto()


class Click:
    __match_args__ = ("position", "button")

    def __init__(self, pos, btn):
        self.position = pos
        self.button = btn


class Event:
    def __init__(self, o):
        self._o = o

    def get(self):
        return self._o


T = TypeVar('T')


class Example(Generic[T]):
    @abstractmethod
    def pep634(self, arg: T) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def apm(self, arg: T) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def apm_expression(self, arg: T) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def apm_statement(self, arg: T) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def apm_terse(self, arg: T) -> Optional[str]:
        raise NotImplementedError


examples: List[Type[Example]] = []

T = TypeVar('T', bound=Example)


def example(clazz: Type[T]) -> Type[T]:
    examples.append(clazz)
    return clazz


@example
class MatchingSequences(Example[str]):

    def pep634(self, command):
        match command.split():
            case [action, obj]:
                return f"action={action} obj={obj}"

    def apm(self, command):
        commands = command.split()
        if result := match(commands, ['action' @ _, 'obj' @ _]):
            return f"action={result.action} obj={result.obj}"

    def apm_expression(self, command: str) -> Optional[str]:
        return case(command.split()) \
            .of(['action' @ _, 'obj' @ _], lambda action, obj: f"action={action} obj={obj}") \
            .otherwise(None)

    def apm_statement(self, command: str) -> Optional[str]:
        try:
            match(command.split())
        except Case(['action' @ _, 'obj' @ _]) as result:
            return f"action={result.action} obj={result.obj}"
        except Default:
            return None

    def apm_terse(self, command: str) -> Optional[str]:
        return match(command.split(),
                     [_, _], lambda action, obj: f"action={action} obj={obj}",
                     _, None)


@example
class MatchingMultiplePatterns(Example[str]):

    def pep634(self, command: str) -> Optional[str]:
        match command.split():
            case [action]:
                return f"action={action}"
            case [action, obj]:
                return f"action={action} obj={obj}"

    def apm(self, command: str) -> Optional[str]:
        commands = command.split()
        if result := match(commands, ['action' @ _]):
            return f"action={result.action}"
        if result := match(commands, ['action' @ _, 'obj' @ _]):
            return f"action={result.action} obj={result.obj}"

    def apm_expression(self, command: str) -> Optional[str]:
        return case(command.split()) \
            .of(['action' @ _], lambda action: f"action={action}") \
            .of(['action' @ _, 'obj' @ _], lambda action, obj: f"action={action} obj={obj}") \
            .otherwise(None)

    def apm_statement(self, command: str) -> Optional[str]:
        try:
            match(command.split())
        except Case(['action' @ _]) as result:
            return f"action={result.action}"
        except Case(['action' @ _, 'obj' @ _]) as result:
            return f"action={result.action} obj={result.obj}"
        except Default:
            return None

    def apm_terse(self, command: str) -> Optional[str]:
        return match(command.split(),
                     [_], lambda action: f"action={action}",
                     [_, _], lambda action, obj: f"action={action} obj={obj}",
                     _, None)


@example
class MatchingSpecificValues(Example[str]):

    def pep634(self, command: str) -> Optional[str]:
        match command.split():
            case ["quit"]:
                return "print=Goodbye!"
            case ["look"]:
                return "look()"
            case ["get", obj]:
                return f"get={obj}"
            case ["go", direction]:
                return f"go={direction}"

    def apm(self, command: str) -> Optional[str]:
        commands = command.split()
        if match(commands, ['quit']):
            return "print=Goodbye!"
        if match(commands, ['look']):
            return "look()"
        if result := match(commands, ['get', 'obj' @ _]):
            return f"get={result.obj}"
        if result := match(commands, ['go', 'direction' @ _]):
            return f"go={result.direction}"

    def apm_expression(self, command: str) -> Optional[str]:
        return case(command.split()) \
            .of(['quit'], "print=Goodbye!") \
            .of(['look'], "look()") \
            .of(['get', 'obj' @ _], lambda obj: f"get={obj}") \
            .of(['go', 'direction' @ _], lambda direction: f"go={direction}") \
            .otherwise(None)

    def apm_statement(self, command: str) -> Optional[str]:
        try:
            match(command.split())
        except Case(['quit']):
            return "print=Goodbye!"
        except Case(['look']):
            return "look()"
        except Case(['get', 'obj' @ _]) as result:
            return f"get={result.obj}"
        except Case(['go', 'direction' @ _]) as result:
            return f"go={result.direction}"
        except Default:
            pass

    def apm_terse(self, command: str) -> Optional[str]:
        return match(command.split(),
                     ['quit'], "print=Goodbye!",
                     ['look'], "look()",
                     ['get', _], lambda obj: f"get={obj}",
                     ['go', _], lambda direction: f"go={direction}",
                     _, None)


@example
class MatchingMultipleValues(Example[str]):

    def pep634(self, command: str) -> Optional[str]:
        match command.split():
            case ["drop", *objects]:
                return f"drop={','.join(objects)}"

    def apm(self, command: str) -> Optional[str]:
        if result := match(command.split(), ["drop", 'objects' @ Remaining()]):
            return f"drop={','.join(result.objects)}"

    def apm_expression(self, command: str) -> Optional[str]:
        try:
            match(command.split())
        except Case(["drop", 'objects' @ Remaining()]) as result:
            return f"drop={','.join(result.objects)}"
        except Default:
            pass

    def apm_statement(self, command: str) -> Optional[str]:
        return case(command.split()) \
            .of(["drop", 'objects' @ Remaining()], lambda objects: f"drop={','.join(objects)}") \
            .otherwise(None)

    def apm_terse(self, command: str) -> Optional[str]:
        return match(command.split(),
                     ["drop", 'objects' @ Remaining()], lambda objects: f"drop={','.join(objects)}",
                     _, None)


@example
class AddingAWildcard(Example[str]):

    def pep634(self, command: str) -> Optional[str]:
        match command.split():
            case ["quit"]:
                return "quit()"
            case ["go", direction]:
                return f"go={direction}"
            case ["drop", *objects]:
                return f"drop={','.join(objects)}"
            case _:
                return f"Sorry, I couldn't understand {command!r}"

    def apm(self, command: str) -> Optional[str]:
        commands = command.split()
        if match(commands, ["quit"]):
            return "quit()"
        if result := match(commands, ["go", 'direction' @ _]):
            return f"go={result.direction}"
        if result := match(commands, ["drop", 'objects' @ Remaining()]):
            return f"drop={','.join(result.objects)}"
        return f"Sorry, I couldn't understand {command!r}"

    def apm_expression(self, command: str) -> Optional[str]:
        return case(command.split()) \
            .of(["quit"], "quit()") \
            .of(["go", 'direction' @ _], lambda direction: f"go={direction}") \
            .of(["drop", 'objects' @ Remaining()], lambda objects: f"drop={','.join(objects)}") \
            .otherwise(f"Sorry, I couldn't understand {command!r}")

    def apm_statement(self, command: str) -> Optional[str]:
        try:
            match(command.split())
        except Case(["quit"]):
            return "quit()"
        except Case(["go", 'direction' @ _]) as result:
            return f"go={result.direction}"
        except Case(["drop", 'objects' @ Remaining()]) as result:
            return f"drop={','.join(result.objects)}"
        except Default:
            return f"Sorry, I couldn't understand {command!r}"

    def apm_terse(self, command: str) -> Optional[str]:
        return match(command.split(),
                     ["quit"], "quit()",
                     ["go", _], lambda direction: f"go={direction}",
                     ["drop", 'objects' @ Remaining()], lambda objects: f"drop={','.join(objects)}",
                     f"Sorry, I couldn't understand {command!r}")


@example
class OrPatterns(Example[str]):

    def pep634(self, command: str) -> Optional[str]:
        match command.split():
            case ["north"] | ["go", "north"]:
                return "go=north"
            case ["get", obj] | ["pick", "up", obj] | ["pick", obj, "up"]:
                return f"get={obj}"

    def apm(self, command: str) -> Optional[str]:
        commands = command.split()
        if match(commands, OneOf(["north"], ["go", "north"])):
            return "go=north"
        if result := match(commands, OneOf(["get", 'obj' @ _], ["pick", "up", 'obj' @ _], ["pick", 'obj' @ _, "up"])):
            return f"get={result.obj}"

    def apm_expression(self, command: str) -> Optional[str]:
        try:
            match(command.split())
        except Case(OneOf(["north"], ["go", "north"])):
            return "go=north"
        except Case(OneOf(["get", 'obj' @ _], ["pick", "up", 'obj' @ _], ["pick", 'obj' @ _, "up"])) as result:
            return f"get={result.obj}"
        except Default:
            pass

    def apm_statement(self, command: str) -> Optional[str]:
        return case(command.split()) \
            .of(OneOf(["north"], ["go", "north"]), "go=north") \
            .of(OneOf(["get", 'obj' @ _], ["pick", "up", 'obj' @ _], ["pick", 'obj' @ _, "up"]),
                lambda obj: f"get={obj}") \
            .otherwise(None)

    def apm_terse(self, command: str) -> Optional[str]:
        return match(command.split(),
                     OneOf(["north"], ["go", "north"]), "go=north",
                     OneOf(["get", 'obj' @ _], ["pick", "up", 'obj' @ _], ["pick", 'obj' @ _, "up"]),
                     lambda obj: f"get={obj}",
                     None)


@example
class CapturingMatchedSubPatterns(Example[str]):

    def pep634(self, command: str) -> Optional[str]:
        match command.split():
            case ["go", ("north" | "south" | "east" | "west") as direction]:
                return f"go={direction}"

    def apm(self, command: str) -> Optional[str]:
        if result := match(command.split(), ["go", 'direction' @ OneOf("north", "south", "east", "west")]):
            return f"go={result.direction}"

    def apm_expression(self, command: str) -> Optional[str]:
        return case(command.split()) \
            .of(["go", 'direction' @ OneOf("north", "south", "east", "west")], lambda direction: f"go={direction}") \
            .otherwise(None)

    def apm_statement(self, command: str) -> Optional[str]:
        try:
            match(command.split())
        except Case(["go", 'direction' @ OneOf("north", "south", "east", "west")]) as result:
            return f"go={result.direction}"
        except Default:
            pass

    def apm_terse(self, command: str) -> Optional[str]:
        return match(command.split(),
                     ["go", 'direction' @ OneOf("north", "south", "east", "west")], lambda direction: f"go={direction}",
                     None)


@example
class AddingConditionsToPatterns(Example[str]):

    def pep634(self, command: str) -> Optional[str]:
        match command.split():
            case ["go", direction] if direction in ('north', 'south'):
                return f"go={direction}"
            case ["go", _]:
                return "Sorry, you can't go that way"

    def apm(self, command: str) -> Optional[str]:
        commands = command.split()
        if (result := match(commands, ["go", ('direction' @ _)])) and result.direction in ('north', 'south'):
            return f"go={result.direction}"
        if match(commands, ["go", _]):
            return "Sorry, you can't go that way"

    def apm_expression(self, command: str) -> Optional[str]:
        return case(command.split()) \
            .of(["go", 'direction' @ _],
                when=lambda direction: direction in ('north', 'south'),
                then=lambda direction: f"go={direction}") \
            .of(["go", _], "Sorry, you can't go that way") \
            .otherwise(None)

    def apm_statement(self, command: str) -> Optional[str]:
        try:
            match(command.split())
        except Case(["go", 'direction' @ _], when=lambda direction: direction in ('north', 'south')) as result:
            return f"go={result.direction}"
        except Case(["go", _]):
            return "Sorry, you can't go that way"
        except Default:
            pass

    def apm_terse(self, command: str) -> Optional[str]:
        raise NotImplementedError


@example
class MatchingPositionalAttributes(Example[Event]):

    def pep634(self, event: Event) -> Optional[str]:
        match event.get():
            case Click((x, y)):
                return f"handle_click({x}, {y})"

    def apm(self, event: Event) -> Optional[str]:
        if result := match(event.get(), Object(Click, ('x' @ _, 'y' @ _))):
            return f"handle_click({result.x}, {result.y})"

    def apm_expression(self, event: Event) -> Optional[str]:
        return case(event.get()) \
            .of(Object(Click, ('x' @ _, 'y' @ _)), lambda x, y: f"handle_click({x}, {y})") \
            .otherwise(None)

    def apm_statement(self, event: Event) -> Optional[str]:
        try:
            match(event.get())
        except Case(Object(Click, ('x' @ _, 'y' @ _))) as result:
            return f"handle_click({result.x}, {result.y})"
        except Default:
            pass

    def apm_terse(self, event: Event) -> Optional[str]:
        return match(event.get(),
                     Object(Click, ('x' @ _, 'y' @ _)), lambda x, y: f"handle_click({x}, {y})",
                     None)


@example
class MatchingAgainstConstantsAndEnums(Example[Event]):

    def pep634(self, event: Event) -> Optional[str]:
        match event.get():
            case Click((x, y), button=Button.LEFT):  # This is a left click
                return f"handle_click({x}, {y})"
            case Click():
                return "ignore_other_clicks"

    def apm(self, event: Event) -> Optional[str]:
        if result := match(event.get(), Object(Click, ('x' @ _, 'y' @ _), button=Button.LEFT)):
            return f"handle_click({result.x}, {result.y})"
        if match(event.get(), Object(Click)):
            return "ignore_other_clicks"

    def apm_expression(self, event: Event) -> Optional[str]:
        return case(event.get()) \
            .of(Object(Click, ('x' @ _, 'y' @ _), button=Button.LEFT), lambda x, y: f"handle_click({x}, {y})") \
            .of(Object(Click), "ignore_other_clicks") \
            .otherwise(None)

    def apm_statement(self, event: Event) -> Optional[str]:
        try:
            match(event.get())
        except Case(Object(Click, ('x' @ _, 'y' @ _), button=Button.LEFT)) as result:
            return f"handle_click({result.x}, {result.y})"
        except Case(Object(Click)):
            return "ignore_other_clicks"
        except Default:
            pass

    def apm_terse(self, event: Event) -> Optional[str]:
        return match(event.get(),
                     Object(Click, ('x' @ _, 'y' @ _), button=Button.LEFT), lambda x, y: f"handle_click({x}, {y})",
                     Object(Click), "ignore_other_clicks",
                     None)


@example
class GoingToTheCloudMapping(Example[dict]):

    def pep634(self, action: dict) -> Optional[str]:
        match action:
            case {"text": message, "color": c}:
                return f"set_text_color({c}); display('{message}');"
            case {"sleep": duration}:
                return f"wait({duration});"
            case {"sound": url, "format": "ogg"}:
                return f"play('{url}');"
            case {"sound": _, "format": _}:
                return "warning: unsupported audio format"

    def apm(self, action: dict) -> Optional[str]:
        if result := match(action, {"text": 'message' @ _, "color": 'c' @ _}):
            return f"set_text_color({result.c}); display('{result.message}');"
        if result := match(action, {"sleep": 'duration' @ _}):
            return f"wait({result.duration});"
        if result := match(action, {"sound": 'url' @ _, "format": "ogg"}):
            return f"play('{result.url}');"
        if match(action, {"sound": _, "format": _}):
            return "warning: unsupported audio format"

    def apm_expression(self, action: dict) -> Optional[str]:
        return case(action) \
            .of({"text": 'message' @ _, "color": 'c' @ _},
                lambda c, message: f"set_text_color({c}); display('{message}');") \
            .of({"sleep": 'duration' @ _},
                lambda duration: f"wait({duration});") \
            .of({"sound": 'url' @ _, "format": "ogg"},
                lambda url: f"play('{url}');") \
            .of({"sound": _, "format": _},
                "warning: unsupported audio format") \
            .otherwise(None)

    def apm_statement(self, action: dict) -> Optional[str]:
        try:
            match(action)
        except Case({"text": 'message' @ _, "color": 'c' @ _}) as result:
            return f"set_text_color({result.c}); display('{result.message}');"
        except Case({"sleep": 'duration' @ _}) as result:
            return f"wait({result.duration});"
        except Case({"sound": 'url' @ _, "format": "ogg"}) as result:
            return f"play('{result.url}');"
        except Case({"sound": _, "format": _}):
            return "warning: unsupported audio format"
        except Default:
            pass

    def apm_terse(self, action: dict) -> Optional[str]:
        return match(action,
                     {"text": 'message' @ _, "color": 'c' @ _},
                     lambda c, message: f"set_text_color({c}); display('{message}');",
                     {"sleep": 'duration' @ _}, lambda duration: f"wait({duration});",
                     {"sound": 'url' @ _, "format": "ogg"}, lambda url: f"play('{url}');",
                     {"sound": _, "format": _}, "warning: unsupported audio format",
                     None)


@example
class MatchingBuiltinClasses(Example[dict]):

    def pep634(self, action: dict) -> Optional[str]:
        match action:
            case {"text": str(message), "color": str(c)}:
                return f"set_text_color({c}); display('{message}');"
            case {"sleep": float(duration)}:
                return f"wait({duration});"
            case {"sound": str(url), "format": "ogg"}:
                return f"play('{url}');"
            case {"sound": _, "format": _}:
                return "warning: unsupported audio format"

    def apm(self, action: dict) -> Optional[str]:
        if result := match(action, {"text": 'message' @ InstanceOf(str), "color": 'c' @ InstanceOf(str)}):
            return f"set_text_color({result.c}); display('{result.message}');"
        if result := match(action, {"sleep": 'duration' @ InstanceOf(float)}):
            return f"wait({result.duration});"
        if result := match(action, {"sound": 'url' @ InstanceOf(str), "format": "ogg"}):
            return f"play('{result.url}');"
        if match(action, {"sound": _, "format": _}):
            return "warning: unsupported audio format"

    def apm_expression(self, action: dict) -> Optional[str]:
        return case(action) \
            .of({"text": 'message' @ InstanceOf(str), "color": 'c' @ InstanceOf(str)},
                lambda c, message: f"set_text_color({c}); display('{message}');") \
            .of({"sleep": 'duration' @ InstanceOf(float)},
                lambda duration: f"wait({duration});") \
            .of({"sound": 'url' @ InstanceOf(str), "format": "ogg"},
                lambda url: f"play('{url}');") \
            .of({"sound": _, "format": _},
                "warning: unsupported audio format") \
            .otherwise(None)

    def apm_statement(self, action: dict) -> Optional[str]:
        try:
            match(action)
        except Case({"text": 'message' @ InstanceOf(str), "color": 'c' @ InstanceOf(str)}) as result:
            return f"set_text_color({result.c}); display('{result.message}');"
        except Case({"sleep": 'duration' @ InstanceOf(float)}) as result:
            return f"wait({result.duration});"
        except Case({"sound": 'url' @ InstanceOf(str), "format": "ogg"}) as result:
            return f"play('{result.url}');"
        except Case({"sound": _, "format": _}):
            return "warning: unsupported audio format"
        except Default:
            pass

    def apm_terse(self, action: dict) -> Optional[str]:
        return match(action,
                     {"text": 'message' @ InstanceOf(str), "color": 'c' @ InstanceOf(str)},
                     lambda c, message: f"set_text_color({c}); display('{message}');",
                     {"sleep": 'duration' @ InstanceOf(float)}, lambda duration: f"wait({duration});",
                     {"sound": 'url' @ InstanceOf(str), "format": "ogg"}, lambda url: f"play('{url}');",
                     {"sound": _, "format": _}, "warning: unsupported audio format",
                     None)


@example
class Literals(Example[int]):
    def pep634(self, status: int) -> Optional[str]:
        match status:
            case 400:
                return "Bad request"
            case 404:
                return "Not found"
            case 418:
                return "I'm a teapot"
            case _:
                return "Something's wrong with the Internet"

    def apm_expression(self, status: int) -> Optional[str]:
        return case(status) \
            .of(400, "Bad request") \
            .of(404, "Not found") \
            .of(418, "I'm a teapot") \
            .otherwise("Something's wrong with the Internet")


@example
class CombineSeveralPatterns(Example[int]):
    def pep634(self, status: int) -> Optional[str]:
        match status:
            case 401 | 403 | 404:
                return "Not allowed"

    def apm(self, status: int) -> Optional[str]:
        if match(status, OneOf(401, 403, 404)):
            return "Not allowed"


@example
class BindVariables(Example[Point]):
    def pep634(self, point: Point) -> Optional[str]:
        match point:
            case Point(0, 0):
                return "Origin"
            case Point(0, y):
                return f"Y={y}"
            case Point(x, 0):
                return f"X={x}"
            case Point(x, y):
                return f"X={x}, Y={y}"
            case _:
                return "## Not a point"

    def apm(self, point: Point) -> Optional[str]:
        if match(point, Point(0, 0)):
            return "Origin"
        if result := match(point, Point(0, 'y' @ _)):
            return f"Y={result.y}"
        if result := match(point, Point('x' @ _, 0)):
            return f"X={result.x}"
        if result := match(point, Point('x' @ _, 'y' @ _)):
            return f"X={result.x}, Y={result.y}"


@example
class ListOfPoints(Example[list]):
    def pep634(self, points: list) -> Optional[str]:
        match points:
            case []:
                return "No points"
            case [Point(0, 0)]:
                return "The origin"
            case [Point(x, y)]:
                return f"Single point {x}, {y}"
            case [Point(0, y1), Point(0, y2)]:
                return f"Two on the Y axis at {y1}, {y2}"
            case _:
                return "Something else"

    def apm(self, points: list) -> Optional[str]:
        if match(points, []):
            return "No points"
        if match(points, [Point(0, 0)]):
            return "The origin"
        if result := match(points, [Point('x' @ _, 'y' @ _)]):
            return f"Single point {result.x}, {result.y}"
        if result := match(points, [Point(0, 'y1' @ _), Point(0, 'y2' @ _)]):
            return f"Two on the Y axis at {result.y1}, {result.y2}"
        return "Something else"


# noinspection PyShadowingNames
def run_examples():
    args = {
        str: [
            "quit",
            "exit",
            "go north",
            "go south",
            "go east",
            "go west",
            "go up",
            "go down",
            "north",
            "south",
            "get sword",
            "pick up sword",
            "pick helmet up",
            "drop sword",
            "drop crossbow dagger helmet",
        ],
        Event: [
            Event(Click((0, 1), Button.LEFT)),
            Event(Click((0, 1), Button.RIGHT)),
        ],
        dict: [
            {"text": "The shop keeper says 'Ah! We have Camembert, yes sir'", "color": "blue"},
            {"sleep": 3},
            {"sleep": 3.0},
            {"sound": "filename.ogg", "format": "ogg"},
            {"sound": "filename.mp3", "format": "mp3"},
        ],
        Point: [
            Point(0, 0),
            Point(0, 1),
            Point(1, 0),
            Point(1, 1),
            Point(1, 2),
            Point(2, 1),
            Point(2, 2),
        ],
        list: [
            [],
            [Point(0, 0)],
            [Point(1, 0)],
            [Point(0, 2), Point(0, 3)],
            [Point(2, 3), Point(0, 3)],
        ],
        int: [
            *range(400, 419)
        ],
    }
    styles = [
        Example.pep634,
        Example.apm,
        Example.apm_expression,
        Example.apm_statement,
        Example.apm_terse,
    ]

    def print_detailed(*args):
        """a stub to pass the time"""

    if DETAILED:
        print_detailed = print
    for example in examples:
        print(f"\n👉 {example.__name__} 👈")
        all_timings = {}
        kind, = get_args(example.__orig_bases__[0])
        for obj in args[kind]:
            ex = example()
            results = dict()
            timings = dict()
            for style in styles:
                func = getattr(ex, style.__name__)
                try:
                    result = func(obj)
                    time = timeit(lambda: func(obj), number=ROUNDS)
                except MatchError:
                    result = '## match error not handled'
                except NotImplementedError:
                    result = NoValue
                except Exception as exc:
                    result = f'## exception: {exc}'
                if result is not NoValue:
                    results[style.__name__] = result
                    # noinspection PyUnboundLocalVariable
                    timings[style.__name__] = time
                    if style.__name__ not in all_timings:
                        all_timings[style.__name__] = 0
                    all_timings[style.__name__] += time
            result = {*results.values()}
            if len(result) != 1:
                print(" ", "❌", f"Different results on {example.__name__} for '{obj}':")
                result = [*result]
                icons = ["🤎", "🧡", "💙", "💜", "💛"]
                for cmd, res in results.items():
                    print(" ", icons[result.index(res)], f"{cmd} → {res}")
            else:
                print_detailed(" ", "✅", f"{example.__name__}: {obj} → {next(iter(result))}")
            second_best = sorted(timings.values())[:2][-1]
            print_detailed(" ", "📈", ', '.join(
                s for s, _ in sorted([(f"{m}: {round(t / second_best, 3)}", t) for m, t in timings.items()],
                                     key=lambda t: t[1])))
        second_best = sorted(all_timings.values())[:2][-1]
        print("📉", ', '.join(
            s for s, _ in sorted([(f"{m}: {round(t / second_best, 3)}", t) for m, t in all_timings.items()],
                                 key=lambda t: t[1])))


if __name__ == '__main__':
    run_examples()
