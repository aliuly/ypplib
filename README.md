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
- `$<key>` and `$$` to escape.  Non resolvable references are not
  substituted.
- password generator:
  - `$<pwgen:options>`
- ssh key generator:
  - `$<keygen:options>`
  - `$<sshkey:options>`
  - `#sshkey args`
  - `#keygen args`
- `#ifdef`, `#ifndef`, `#else`, `#endif`
- `#exec`, `#error`, `#warn`

Things to try:

- doctests
- unittests


```python
  elif args.excmd == K.PWGEN:
    pwlen = 8
    chrset = ''
    count = 8
    for opts in args.define:
      if opts.lower() == K.UPPER:
        chrset += string.ascii_uppercase
      elif opts.lower() == K.LOWER:
        chrset += string.ascii_lowercase
      elif opts.lower() == K.DIGITS:
        chrset += string.digits
      elif opts.lower().startswith(K.PWLEN + '='):
        pwlen = int(opts[len(K.PWLEN)+1:])
      elif opts.lower().startswith('n='):
        count = int(opts[2:])
    if chrset == '': chrset = string.ascii_uppercase + string.ascii_lowercase + string.digits
    for i in range(count):
      print(ypp.pwhash.gen_rand(pwlen, chrset))
```
