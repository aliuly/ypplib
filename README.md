# ypplib

YAML pre-processor library

- delayed variable substitution
- configuration
  - defaults from application
  - read defaults from config ini
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

  
