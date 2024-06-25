#!/usr/bin/env python3
'''Config file loader
'''

import re

import ipp

# parse config lines
RE_CONFIG_LINE = re.compile(r'^([_A-Za-z][_A-Za-z0-9]*)\s*(:|=)\s*')
'''regexp used to parse configuration file lines'''

def load_config(cfg_file:str, yppi:ipp.iYamlPreProcessor) -> None:
  '''Load configuration file

  :param cfg_file: config file name
  :param yppi: Yaml Pre processor instance

  `yppi` variables are modified.

  Parses a simple configuration file.  It has the following specifications:

  - lines beginning with `#` or `;` are comments (ignored)
  - `key: value`  define `key` as `value`.  `value` can contain variable
    substitions that are evaluated immediatly
  - `key = value` define `key` as `value`.  Variable substition
     evalutions are delayed

  '''
  with open(cfg_file, 'r') as cfg_fp:
    state = yppi.save_state(cfg_file)
    for ln in cfg_fp:
      ln = ln.strip()
      if ln[0] == '#' or ln[0] == ';': continue
      mv = RE_CONFIG_LINE.match(ln)
      if not mv:
        yppi.msg('Unrecognizned config line')
        continue

      if mv.group(2) == ':':
        yppi.define_var(mv.group(1), ln[mv.dend():], True)
      else:
        yppi.define_var(mv.group(1), ln[mv.dend():], False)

    yppi.restore_state(state)

def cb_load(yppi:ipp.iYamlPreProcessor, args:str, prefix:str = '') -> str:
  '''Handler config file loading

  :param yppi: Yaml Pre-Processor instance
  :param args: argument string passed in the pre-processor directive
  :param prefix: used to maintain YAML structure
  '''
  load_config(args, yppi)
  return ''


if __name__ == '__main__':
  pass

