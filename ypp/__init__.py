#!/usr/bin/env python3
''' YAML pre-processor library

'''

import os
import sys
import typing
import yaml

try:
  from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
  ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

saved_path = list(sys.path)
sys.path.append(os.path.dirname(__file__))

from version import VERSION
from process import STR, YamlPreProcessor

sys.path = saved_path
del saved_path

class __meta__:
  name = 'ypplib'
  version = VERSION
  author = 'A Liu Ly'
  author_email = 'alejandrol@t-systems.com'
  description = 'Yaml Pre-Processor library'
  url = 'https://github.com/aliuly/ypplib'
  license = 'MIT'

default_vars = dict()

def init(config:list[str] = [], include:list[str] = [], define:list[str] = [], app_defaults:dict[str] = {}, env_prefix:str = '') -> YamlPreProcessor:
  if len(default_vars) == 0:
    default_vars[VERSION] = YamlPreProcessor(config, include, define, app_defaults, env_prefix)
  return default_vars[VERSION]

def process(fileptr:str|typing.TextIO) -> str:
  if len(default_vars) == 0: raise RuntimeError
  return default_vars[VERSION].process(fileptr)

def load(fileptr:str|typing.TextIO) -> any:
  ytxt = process(fileptr)
  return yaml.safe_load(ytxt)

def lookup(name:str) -> str|None:
  if len(default_vars) == 0: raise RuntimeError
  return default_vars[VERSION].lookup(name)
