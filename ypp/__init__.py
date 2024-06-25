#!/usr/bin/env python3
''' YAML pre-processor library

This library can be used to enhance YAML based configuration
files to also include pre-processor directives and macro
expansions.

This module makes available the {py:obj}`pproc.YamlPreProcessor`
and {py:obj}`pproc.STR` directly.

So you can just:

```python
import ypp

pp = ypp.YamlPreProcessor()
pp.define_var(ypp.STR.SECRETS_FILE,'secrets.ini')
incpath = pp.lookup(ypp.STR.INCLUDE_PATH)

```

Alternatively you can use the procedural interface:

```python
import ypp

pp = ypp.init()
obj = ypp.load('sample.yaml')
inc_path = ypp.lookup(ypp.STR.INCLUDE_PATH)

```


'''

import os
import sys
import typing
import yaml

try:
  from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
  ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

import __meta__

saved_path = list(sys.path)
''' _private_
:meta private:
'''

sys.path.append(os.path.dirname(__file__))

from version import VERSION
from pproc import STR, YamlPreProcessor

sys.path = saved_path
del saved_path


default_vars = dict()
''' _private_
:meta private:

Stores global variables, used in the procedural API.
'''


def init(config:list[str] = [], include:list[str] = [], define:list[str] = [], app_defaults:dict[str] = {}, env_prefix:str = '') -> YamlPreProcessor:
  '''Initialize a pre-processor instance

  :param config: list of configuration files to load
  :param include: list of include directories to add to include path
  :param define: list of `key=value` strings used to initialize pre-processor variables
  :param app_defaults: dictionary of strings used to initialize pre-processor variables
  :param env_prefix: Initialize pre-processor variables with environment variables that start with `env_prefix`.
  :returns: Initialized pre-processor

  Initializes as pre-processor instance.  This is the procedural API
  which only allows for a single pre-processor instance to be used.

  If multiple pre-processor instances are needed, these can be created
  by creating a new {py:obj}`pproc.YamlPreProcessor`  object instance.

  '''
  if len(default_vars) == 0:
    default_vars[VERSION] = YamlPreProcessor(config, include, define, app_defaults, env_prefix)
  return default_vars[VERSION]

def process(fileptr:str|typing.TextIO) -> str:
  '''Process a file or file-pointer

  :param fileptr: a str containing a file name or a TextIO object as returned by `open`
  :returns: pre-processed string
  :raises RuntimeError: If `init` has not been called

  Process the given file or file-pointer using the current
  {py:obj}`pproc.YamlPreProcessor` instance.

  You **must** call `init` before using `process`.

  Multiple calls to `process` will use the same {py:obj}`pproc.YamlPreProcessor`
  instance.  This means that variables defined in previous calls
  to `process` will remain for the duration of the program run.
  '''
  if len(default_vars) == 0: raise RuntimeError
  return default_vars[VERSION].process(fileptr)

def load(fileptr:str|typing.TextIO) -> any:
  '''Load a YAML file or a file-pointer and returns its structure
  :param fileptr: a str containing a file name or a TextIO object as returned by `open`
  :returns: object as specified in the YAML input file
  :raises RuntimeError: If `init` has not been called

  Utility function that calls `process` and subsequently loads its
  output using `yaml.safe_load`.
  '''
  ytxt = process(fileptr)
  return yaml.safe_load(ytxt)

def lookup(name:str) -> str|None:
  '''Returns the value of the given `name`
  :param name: pre-processor variable to look-up
  :raises RuntimeError: If `init` has not been called
  '''
  if len(default_vars) == 0: raise RuntimeError
  return default_vars[VERSION].lookup(name)

def define_var(key:str, value:str, var_expand = False) -> None:
  '''Define a pre-processor variable
  :param key: name of variable to define
  :param value: value to assign to variable
  :param var_expand: if `True` the string in `value` will be evalued for variable expansion.  `False` omits variable expansion (This is the default).
  :raises RuntimeError: If `init` has not been called
  '''
  if len(default_vars) == 0: raise RuntimeError
  default_vars[VERSION].define_var(key, value, var_expand)
