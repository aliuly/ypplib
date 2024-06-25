# ypplib

YAML pre-processor library

- delayed variable substitution
- configuration
  - defaults from application
  - read defaults from config ini
  - read defaults from environment
  - from command line arguments: -D -I
  - in-line defines
- out to file using UNIX or MSDOS newlines
- command line or as embeddable component
- sphinx documentation

Syntax:

- `#define key value`
- `$(key)' and $$ to escape.  Non resolvable references are not
  substituted.
- password generator:\
  `$(PWGEN:options)`
- ssh key gernator:\
  `$(KEYGEN:options)`
- `#ifdef`, `#ifndef`, `#else`, `#endif`
- `#exec`, `#error`, `#warn`

Things to try:

- doctests
- unittests
- use `newline` in open to set the EOL

NOTE:

Macros are of the for `$(something)`.  This is similar to the syntax
in Makefiles.  Unfortunately it overlaps with Shell syntax of
`$(command)`.  Do we switch tosomething like `$<something>`?
