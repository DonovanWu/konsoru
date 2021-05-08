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

import re, argparse, functools, json, os, atexit
from konsoru import CLI
from konsoru.decorators import description

parser = argparse.ArgumentParser()
parser.add_argument('--env', action='store', required=False, default=None, metavar='filename',
                    help='A JSON file that loads and stores environment variables. Start afresh if not given.')
args = parser.parse_args()

env_file = args.env

if env_file is None:
    env = {}
else:
    if os.path.isfile(env_file):
        with open(env_file, 'r') as _fp:
            env = json.load(_fp)
    else:
        print('[WARNING] Environment file does not exist! Generating one with default environment...')
        env = {}

# default environment variables
env['ans'] = env.get('ans',  0)
env['pi'] = env.get('pi',  3.141592653589793)

cli = CLI()


def _save_env():
    if env_file is not None:
        with open(env_file, 'w') as _fp:
            json.dump(env, _fp)

atexit.register(_save_env)


def _store_answer(func):
    global env
    
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        value = func(*args, **kwargs)
        env['ans'] = value
        return value

    return decorator


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


@cli.subroutine()
@_store_answer
def add(a, b):
    a = _parse(a)
    b = _parse(b)
    return a + b


@cli.subroutine()
@_store_answer
def sub(a, b):
    a = _parse(a)
    b = _parse(b)
    return a - b


@cli.subroutine()
@_store_answer
def mul(a, b):
    a = _parse(a)
    b = _parse(b)
    return a * b


@cli.subroutine()
@_store_answer
def div(a, b, floor_div=False):
    a = _parse(a)
    b = _parse(b)
    if floor_div:
        return a // b
    else:
        return a / b


# let's not overwrite the builtin sum()...
@cli.subroutine(name='sum')
@_store_answer
def sum_func(*vals):
    return sum(map(_parse, vals))


@cli.subroutine(name='set')
@description('Set a variable.')
def set_var(name, value):
    global env
    if re.match(r'^[a-zA-Z_$][a-zA-Z_$0-9]*$', name):
        env[name] = _parse(value)
    else:
        raise ValueError('"%s" does not follow variable name rule!' % name)


@cli.subroutine(name='env')
@description('Show all variables.')
def show_env():
    for name, value in env.items():
        print(name, '=', value)


@cli.subroutine()
@description('Show the answer of the previous operation.')
def ans():
    return env['ans']


cli.loop()
