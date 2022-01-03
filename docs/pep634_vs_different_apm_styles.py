from __future__ import annotations

import os
from abc import abstractmethod
from timeit import timeit
from typing import Optional, Type, List, TypeVar

from apm import *

ROUNDS = int(os.environ.get('ROUNDS', '1000'))

DETAILED = bool(os.environ.get('DETAILED', '').lower() in ('yes', 'true', 'on', '1', 'enabled'))


class Example:
    @abstractmethod
    def pep634(self, command: str) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def apm(self, command: str) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def apm_expression(self, command: str) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def apm_statement(self, command: str) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def apm_terse(self, command: str) -> Optional[str]:
        raise NotImplementedError


examples: List[Type[Example]] = []

T = TypeVar('T', bound=Example)


def example(clazz: Type[T]) -> Type[T]:
    examples.append(clazz)
    return clazz


@example
class MatchingSequences(Example):

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
class MatchingMultiplePatterns(Example):

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
class MatchingSpecificValues(Example):

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
class MatchingMultipleValues(Example):

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
class AddingAWildcard(Example):

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
class OrPatterns(Example):

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
class CapturingMatchedSubPatterns(Example):

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
class AddingConditionsToPatterns(Example):

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


class NoResult:
    pass


# noinspection PyShadowingNames
def run_examples():
    commands = [
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
    ]
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
        for command in commands:
            ex = example()
            results = dict()
            timings = dict()
            for style in styles:
                func = getattr(ex, style.__name__)
                try:
                    result = func(command)
                    time = timeit(lambda: func(command), number=ROUNDS)
                except MatchError:
                    result = '## match error not handled'
                except NotImplementedError:
                    result = NoResult
                except Exception as exc:
                    result = f'## exception: {exc}'
                if result is not NoResult:
                    results[style.__name__] = result
                    # noinspection PyUnboundLocalVariable
                    timings[style.__name__] = time
                    if style.__name__ not in all_timings:
                        all_timings[style.__name__] = 0
                    all_timings[style.__name__] += time
            result = {*results.values()}
            if len(result) != 1:
                print(" ", "❌", f"Different results on {example.__name__} for '{command}':")
                result = [*result]
                icons = ["🤎", "🧡", "💙", "💜", "💛"]
                for cmd, res in results.items():
                    print(" ", icons[result.index(res)], f"{cmd} → {res}")
            else:
                print_detailed(" ", "✅", f"{example.__name__}: {command} → {next(iter(result))}")
            second_best = sorted(timings.values())[1]
            print_detailed(" ", "📈", ', '.join(
                s for s, _ in sorted([(f"{m}: {round(t / second_best, 3)}", t) for m, t in timings.items()],
                                     key=lambda t: t[1])))
        second_best = sorted(all_timings.values())[1]
        print("📉", ', '.join(
            s for s, _ in sorted([(f"{m}: {round(t / second_best, 3)}", t) for m, t in all_timings.items()],
                                 key=lambda t: t[1])))


if __name__ == '__main__':
    run_examples()
