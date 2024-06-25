#!/usr/bin/env python3
'''External command executor
'''
import os
import subprocess

import ipp

def cb_exec(yppi:ipp.iYamlPreProcessor, args:str, prefix:str = '') -> str:
  '''Handler for external commands
  
  :param yppi: Yaml Pre-Processor instance
  :param args: argument string passed in the pre-processor directive
  :param prefix: used to maintain YAML structure
  '''
  cwd = None
  filename = yppi.get_filename()
  if filename:
    cwd = os.path.dirname(filename)
    if cwd == ' ': cwd = None

  rc = subprocess.run(args,
                      capture_output=True,
                      shell=True,
                      text=True,
                      cwd=cwd)
  if rc.returncode != 0:
    yppi.msg(f'Command: {args} exited status {rc.returncode}')
  if rc.stderr != '': sys.stderr.write(rc.stderr)

  prefix2 = prefix.replace('-',' ')
  # Used to handle `- #include` syntax
  txt = ''
  for i in rc.stdout.split('\n'):
    txt += prefix + i +'\n'
    prefix = prefix2

  return txt

if __name__ == '__main__':
  pass
  
