#!/usr/bin/env python3
'''Include file handler
'''
import base64
import re

try:
  from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
  ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

import ipp


RE_TYPE = re.compile(r'\s*--(raw|bin)\s+')
''' Regular expression to determine the include type '''

def include_raw(yppi:ipp.iYamlPreProcessor, fname:str, prefix:str) -> str:
  ''' Include file verbatim

  :param yppi: YamlPreProcessor instance
  :param fname: File to include
  :param prefix: lines are prepended with ``prefix``

  Includes a file without doing any pre-processing.  No variable
  expansion nor include statements.

  Prefix is still used.  This is to maintiain the YAML file structure.
  '''
  txt = ''
  fname = yppi.find_include(fname)
  prefix2 = prefix.replace('-',' ')
  # We do this to allow `- #include` syntax  

  with open(fname,'r') as f:
    for line in f:
      if line.endswith("\n"): line = line[:-1]
      if line.endswith("\r"): line = line[:-1]
      txt += prefix + line + "\n"
      prefix = prefix2
  return txt

def include_bin(yppi:ipp.iYamlPreProcessor, fname:str, prefix:str) -> str:
  ''' Include binary file

  :param yppi: YamlPreProcessor instance
  :param fname: File to include
  :param prefix: lines are prepended with ``prefix``

  Include binary file as MIME/Base64 encoded text.

  Prefix is used to maintain YAML file structure.
  '''
  txt = ''
  prefix2 = prefix.replace('-',' ')
  # We do this to allow `- #include` syntax  

  fname = yppi.find_include(fname)

  with open(fname,'rb') as f:
    b64 = base64.b64encode(f.read()).decode('ascii')
    i = 0
    while i < len(b64):
      txt += prefix + b64[i:i+76] + "\n"
      prefix = prefix2
      i += 76

  return txt

def cb_inc(yppi:ipp.iYamlPreProcessor, args:str, prefix:str = '') -> str:
  '''Handler for external commands
  
  :param yppi: Yaml Pre-Processor instance
  :param args: argument string passed in the pre-processor directive
  :param prefix: used to maintain YAML structure
  '''
  # ~ ic(args)
  try:
    mv = RE_TYPE.match(args)
    if mv:
      args = args[mv.end():]
      if mv.group(1) == 'raw':
        return include_raw(yppi, args, prefix)
      elif mv.group(1) == 'bin':
        return include_bin(yppi, args, prefix)
    return yppi.read_file(args, prefix)
  except FileNotFoundError as e:
    yppi.msg(str(e))
    return ''

if __name__ == '__main__':
  pass
  

