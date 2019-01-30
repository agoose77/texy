import typing
from collections import deque
from contextlib import contextmanager
from enum import Enum, auto
from io import StringIO, TextIOBase
import textwrap


class Operations(Enum):
    REQUIRED = auto()
    OPTIONAL = auto()
    LEAVE_ENV = auto()
    ENTER_ENV = auto()
    NAME = auto()
    TEXT = auto()


class ArgumentBundle(typing.NamedTuple):
    args: typing.List[str]
    kwargs: typing.Dict[str, str]


def _(*args, **kwargs):
    return ArgumentBundle(args, kwargs)


class _LaTeXMacroProxy:

    def __init__(self, stack: typing.Deque[tuple]):
        self._stack = stack

    def __call__(self, *args, **kwargs) -> '_LaTeXMacroProxy':
        """Implement the """
        self._stack.append((Operations.REQUIRED, args, kwargs))
        return self

    def __getitem__(self, args) -> '_LaTeXMacroProxy':
        kwargs = {}
        if isinstance(args, str):
            args = (args,)

        elif isinstance(args, ArgumentBundle):
            args, kwargs = args

        self._stack.append((Operations.OPTIONAL, args, kwargs))
        return self

    def __enter__(self) -> '_LaTeXMacroProxy':
        temp_stack = []

        while True:
            token = self._stack.pop()
            temp_stack.append(token)
            if token[0] == Operations.NAME:
                break

        self._stack.append((Operations.ENTER_ENV,))

        while temp_stack:
            self._stack.append(temp_stack.pop())

        return self

    def __exit__(self, type, value, traceback):
        self._stack.append((Operations.LEAVE_ENV,))
        return


class _LaTeXProxy:

    def __init__(self, stack: typing.Deque[tuple]):
        self._stack = stack
        self._proxy = _LaTeXMacroProxy(self._stack)

    def __getattr__(self, name: str) -> _LaTeXMacroProxy:
        self._stack.append((Operations.NAME, name))
        return self._proxy

    def __call__(self, text) -> '_LaTeXProxy':
        """Implement the """
        self._stack.append((Operations.TEXT, text))


def format_params(args: typing.Sequence[str], kwargs: typing.Mapping[str, str]) -> str:
    arg_strings = [str(a) for a in args]
    kwarg_strings = [f"{k}={v}" for k, v in kwargs.items()]
    all_args = [*arg_strings, *kwarg_strings]
    if not all_args:
        return ""

    return ", ".join(all_args)


def write_operation_stack(stack: typing.Deque[tuple], stream: TextIOBase, indent_depth: int):
    environment_stack = []

    def indent():
        return len(environment_stack) * indent_depth * " "

    while stack:
        token_type, *params = stack.popleft()

        if token_type == Operations.ENTER_ENV:
            name_token_type, name = stack.popleft()
            assert name_token_type == Operations.NAME

            stream.write(f"\n{indent()}\\begin{{{name}}}")
            environment_stack.append(name)

        elif token_type == Operations.LEAVE_ENV:
            name = environment_stack.pop()
            stream.write(f"\n{indent()}\\end{{{name}}}")

        elif token_type == Operations.NAME:
            name, = params
            stream.write(f"\n{indent()}\\{name}")

        elif token_type == Operations.OPTIONAL:
            args, kwargs = params
            stream.write(f"[{format_params(args, kwargs)}]")

        elif token_type == Operations.REQUIRED:
            args, kwargs = params
            stream.write(f"{{{format_params(args, kwargs)}}}")

        elif token_type == Operations.TEXT:
            text, = params

            stream.write("\n")
            stream.write(textwrap.indent(text, indent()))

        else:
            raise ValueError(token_type)


@contextmanager
def latex(indent_depth: int = 4, stream: TextIOBase = None):
    stack = deque()
    yield _LaTeXProxy(stack)

    should_print_output = stream is None
    if stream is None:
        stream = StringIO()

    write_operation_stack(stack, stream, indent_depth)

    if should_print_output:
        print(stream.getvalue())


if __name__ == "__main__":
    with latex() as t:
        t("HI")
        with t.figure['h!']:
            t.includegraphics[_(width=r'\textwidth')]('some_fig.png')
            t.caption('Some Caption')
