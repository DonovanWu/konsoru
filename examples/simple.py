"""
A simple calculator example to demonstrate the basics of konsoru framework.

Demo
----------------
bash-3.2$ python3 examples/simple.py
Type 'help' to see help message.
Type 'quit' or 'exit' to exit the program.
> help
Available commands:
    add       ans       div       env       exit      help
    mul       quit      set       sub       sum
See help for a specific command by specifying the command name.
Help message for multi-layered command can still be seen by using quotation marks around them.
> help add
usage: add [-h] a b

positional arguments:
  a
  b

optional arguments:
  -h, --help  show this help message and exit

> help env
usage: env [-h]

Show all variables.

optional arguments:
  -h, --help  show this help message and exit

> add 2 3
5
> sum 1 2 3 4 5
15
> div 3 2
1.5
> div 3 2 --floor_div
1
> set a 5
> env
ans = 1
pi = 3.141592653589793
a = 5
> sub a 1.5
3.5
> quit
"""

import re
from konsoru import CLI
from konsoru.decorators import description

env = {
    'ans': 0,
    'pi': 3.141592653589793,
}


def _print_and_store(value):
    global env
    print(value)
    env['ans'] = value


def _parse(s):
    global env
    if re.match(r'^[a-zA-Z_$][a-zA-Z_$0-9]*$', s):
        # match variable name rule
        if s in env:
            return env[s]
        else:
            raise ValueError('Variable "%s" not set yet!' % s)
    elif re.match(r'^[1-9]\d*(?:\.\d+)?$', s):
        # match numbers
        if '.' in s:
            return float(s)
        else:
            return int(s)
    raise ValueError('"%s" does not follow variable name rule!' % s)


def add(a, b):
    a = _parse(a)
    b = _parse(b)
    _print_and_store(a + b)


def sub(a, b):
    a = _parse(a)
    b = _parse(b)
    _print_and_store(a - b)


def mul(a, b):
    a = _parse(a)
    b = _parse(b)
    _print_and_store(a * b)


def div(a, b, floor_div=False):
    a = _parse(a)
    b = _parse(b)
    if floor_div:
        _print_and_store(a // b)
    else:
        _print_and_store(a / b)


# let's not overwrite the builtin sum()...
def sum_func(*vals):
    _print_and_store(sum(map(_parse, vals)))


@description('Set a variable.')
def set_var(name, value):
    global env
    if re.match(r'^[a-zA-Z_$][a-zA-Z_$0-9]*$', name):
        env[name] = _parse(value)
    else:
        raise ValueError('"%s" does not follow variable name rule!' % name)


@description('Show all variables.')
def show_env():
    for name, value in env.items():
        print(name, '=', value)


@description('Show the answer of the previous operation.')
def ans():
    _print_and_store(env['ans'])


cli = CLI()
cli.add_function(add)
cli.add_function(sub)
cli.add_function(mul)
cli.add_function(div)
cli.add_function(ans)
cli.add_function(sum_func, name='sum')
cli.add_function(set_var, name='set')
cli.add_function(show_env, name='env')
cli.loop()
