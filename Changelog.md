Changelog
=========

## v0.1.0

New Features:
1. Added subroutine decorator (same function as `add_function()`).
2. Added a feature to print function return automatically, enabled by default.

Bug Fixes:
1. Fixed a tab completion bug on Mac. (The fix in the last version was ineffective.)

## v0.0.7

Bug Fixes:
1. Fixed a tab completion bug on Mac.

## v0.0.6

New Features:
1. Added one exception for developers to use.

Improvements:
1. Corrected some mistakes in docstrings.
2. Changed password reading method from TerminalMode to Python's "getpass" module,
so that it can also be used in Windows.

## v0.0.5

New Features:
1. Added an option to add main function to "run" when no subcommand is given.

Improvements:
1. Now default commands (help, quit, exit) are no longer added in "run" mode.

## v0.0.4

New Features:
1. Added function "run" to CLI class to run command once and exit (more traditional CLI framework capability).

## v0.0.3

New Features:
1. Added an option to expand asterisk into file names just like shell does.
2. Added "tee" and "sed" to default allowed unix commands.
3. Added a hidden CLI class method "list_shell_commands".

Bug Fixes:
1. Fixed a bug with appendable argument that happens when no argument is provided.

## v0.0.2

Improvements:
1. Fixed some erroneous docstring.

## v0.0.1

Initial release.
