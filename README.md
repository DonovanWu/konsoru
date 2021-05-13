Konsoru
=======

A functional programming styled CLI console application framework based on argparse.

## Installation

The easiest way to install konsoru is to use [pip](https://pip.pypa.io/en/stable/installing/):

```bash
$ pip install konsoru
```

## Usage

Konsoru enables you to build CLI applications quickly: either a text-based console or a program with multiple subcommands that executes in terminal.

Below is a bare minimum `helloworld.py` program that launches a text-based console:

```python
from konsoru import CLI

def helloworld():
    print('Hello world!')

cli = CLI()
cli.add_function(helloworld)
cli.loop()
```

The console comes with 3 default commands: help, quit, exit. And every command added into the console, including default commands, will come with a `-h` option that displays its help message.

When the above program runs, it looks like this:

```
$ python3 helloworld.py 
Type 'help' to see help message.
Type 'quit' or 'exit' to exit the program.
> help
Available commands:
    exit        helloworld  help        quit        
See help for a specific command by specifying the command name.
Help message for multi-layered command can still be seen by using quotation marks around them.
> helloworld -h
usage: helloworld [-h]

optional arguments:
  -h, --help  show this help message and exit
> helloworld
Hello world!
> quit
```

Alternatively, you can add your function as a command using the `subroutine()` decorator. The decorator should be stacked on top of other decorators, if any. Also, by default, the framework will print the return of added functions, unless the return is `None`. So the program below is completely equivalent to the example above:

```python
from konsoru import CLI

cli = CLI()

@cli.subroutine()
def helloworld():
    return 'Hello world!'

cli.loop()
```

To convert this into a program with subcommands that is interacted with through terminal, simply change `cli.loop()` into `cli.run()` at the end. Then, the program will behave like this:

```
$ python3 helloworld.py helloworld
Hello world!
```

Note that default commands under the console mode, i.e. `help`, `exit`, `quit`, will not be added when using `cli.run()`.

Put the script in a directory in your `$PATH` and give it executable permissions to call it anywhere in your filesystem without `python3` in the front.

For more sophisticated examples, check the `examples/` directory in the github repository.
