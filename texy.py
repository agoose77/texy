from io import StringIO
from collections import deque
from contextlib import contextmanager


_stack = deque()


def push_token(token):
    _stack.append(token)


def pop_token():
    return _stack.pop()


def popleft_token():
    return _stack.popleft()


class Operable:

    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        push_token(('required', args, kwargs))
        return self

    def _(self, *args, **kwargs):
        push_token(('optional', args, kwargs))
        return self

    def __enter__(self):
        temp_stack = []

        while True:
            token = pop_token()
            temp_stack.append(token)
            if token[0] == 'name':
                break

        push_token(('enter_env',))

        while temp_stack:
            push_token(temp_stack.pop())

        return self

    def __exit__(self, type, value, traceback):
        push_token(('leave_env',))
        return self


class _Latex:

    def __init__(self,):
        self._operable = Operable()

    def __getattr__(self, name):
        push_token(('name', name))
        return self._operable


def format_params(args, kwargs):
    arg_strings = [str(a) for a in args]
    kwarg_strings = [f"{k}={v}" for k, v in kwargs.items()]
    all_args = [*arg_strings, *kwarg_strings]
    if not all_args:
        return ''

    return ', '.join(all_args)

def write_stack(stream, indent_depth):
    env_stack = []

    def indent():
        return len(env_stack) * indent_depth * ' '

    while _stack:
        token = (token_type, *params) = popleft_token()

        if token_type == 'enter_env':
            name_token_type, name = popleft_token()
            assert name_token_type == 'name'

            stream.write(f'\n{indent()}\\begin{{{name}}}')
            env_stack.append(name)

        elif token_type == 'leave_env':
            name = env_stack.pop()
            stream.write(f'\n{indent()}\\end{{{name}}}')

        elif token_type == 'name':
            name, = params
            stream.write(f'\n{indent()}\\{name}')

        elif token_type == 'optional':
            args, kwargs = params
            stream.write(f'[{format_params(args, kwargs)}]')

        elif token_type == 'required':
            args, kwargs = params
            stream.write(f'{{{format_params(args, kwargs)}}}')

        else:
            raise ValueError(token_type)


@contextmanager
def latex(indent_depth=4, stream=None):
    helper = _Latex()
    yield helper
    if stream is None:
        stream = StringIO()
    write_stack(stream, indent_depth)


if __name__ == '__main__':
    from pprint import pprint

    with latex() as t:
        with t.figure._('h!'):
            t.includegraphics._(width=r'\textwidth')('some_fig.png')
            t.caption('Some Caption')
