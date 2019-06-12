"""
A bare minimum example.

How to use this script
------------------------
bash-3.2$ python3 examples/helloworld.py
Type 'help' to see help message.
Type 'quit' or 'exit' to exit the program.
> helloworld
Hello world!
> quit
"""

from konsoru import CLI


def helloworld():
    print('Hello world!')


cli = CLI()
cli.add_function(helloworld)
cli.loop()
