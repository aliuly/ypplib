#!/usr/bin/env python3
''' YAML pre-processor command

If used on the command line, it acts as a pre-processor reading
YAML files with pre-processor directives, and outputs
the processed file.

Optionally it can parse the generated YAML and dump it as a JSON
object (which is also valid YAML document)
'''
import json
import os
import sys
import typing
import yaml

from argparse import ArgumentParser

try:
  from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
  ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))
import ypp

def cmd_cli():
  ''' Command Line Interface argument parser '''
  cli = ArgumentParser(prog='ypp',description='YAML file pre-processor')
  cli.add_argument('-D','--define', help='Add constant', action='append', default=[])
  cli.add_argument('-I','--include', help='Add Include path', action='append', default=[])
  cli.add_argument('-C','--config', help='Read configuration file', action='append', default=[])
  cli.add_argument('-J','--json', help='Parse YAML and dump JSON',action='store_true')
  cli.add_argument('-V','--version', action='version', version='%(prog)s '+ ypp.VERSION)

  cli.add_argument('-o','--output', help='Save output to the given file', default=None)
  cli.add_argument('-n','--no-pp', help='Disable pre-processor',action='store_true')
  cli.add_argument('--unix', help='Force UNIX mode output', action='store_true')
  cli.add_argument('--windows', help='Force Windows mode output', action='store_true')

  cli.add_argument('file', help='YAML file to parse', nargs='*')
  return cli

def load_yaml(text:str|typing.TextIO) -> any:
  try:
    res = yaml.safe_load(text)
  except yaml.parser.ParserError as err:
    sys.stderr.write(f'Yaml Parser error: {err}\n')
    sys.exit(1)
  return res


###################################################################
#
# Main command line
#
###################################################################

if __name__ == '__main__':

  cli = cmd_cli()
  args = cli.parse_args()

  if args.unix and args.windows:
    sys.stderr.write('Options --unix and --windows are mutually exclusive\n')
    sys.exit(52)
  if args.output is None:
    if args.unix or args.windows:
      sys.stderr.write('Options --unix and --windows only allowed when using --output option\n')
      sys.exit(52)
    outfp = sys.stdout
  else:
    if args.unix:
      outfp = open(args.output,'w',newline='\n')
    elif args.windows:
      outfp = open(args.output,'w',newline='\r\n')
    else:
      outfp = open(args.output,'w')

  if args.no_pp:
    if len(args.file) == 0:
      res = load_yaml(sys.stdin)
      if args.json:
        outfp.write(json.dumps(res))
      else:
        outfp.write(yaml.dump(res))      
    else:
      for input_file in args.file:
        with open(input_file, 'r') as fp:
          res = load_yaml(fp)
          if args.json:
            outfp.write(json.dumps(res))
          else:
            outfp.write(yaml.dump(res))
  else:
    ypp.init(args.config, args.include, args.define, {}, '')
    if len(args.file) == 0:
      txt = ypp.process(sys.stdin)
      if args.json:
        res = load_yaml(txt)
        outfp.write(json.dumps(res))
      else:
        outfp.write(txt)
    else:
      for input_file in args.file:
        txt = ypp.process(input_file)
        if args.json:
          res = load_yaml(txt)
          outfp.write(json.dumps(res))
        else:
          outfp.write(txt)

