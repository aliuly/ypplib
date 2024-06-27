#!/usr/bin/env python3
''' YAML pre-processor command line interface

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

if '__file__' in globals():
  sys.path.append(os.path.join(os.path.dirname(__file__),'..'))
import ypp

COMPACT = -1

def cmd_cli():
  ''' Command Line Interface argument parser '''
  cli = ArgumentParser(prog='ypp',description='YAML file pre-processor')
  cli.add_argument('-D','--define', help='Add constant', action='append', default=[])
  cli.add_argument('-I','--include', help='Add Include path', action='append', default=[])
  cli.add_argument('-C','--config', help='Read configuration file', action='append', default=[])
  # ~ cli.add_argument('-J','--json', help='Parse YAML and dump JSON',action='store_true')
  cli.add_argument('-J','--json', help='Parse YAML and dump JSON',
                    action='store',
                    default=None,     # do not generate JSON
                    const=COMPACT,    # indent=None, most compact representation
                    type=int,
                    nargs='?')
  cli.add_argument('-V','--version', action='version', version='%(prog)s '+ ypp.VERSION)

  cli.add_argument('-o','--output', help='Save output to the given file', default=None)
  cli.add_argument('-n','--no-pp', help='Disable pre-processor',action='store_true')
  cli.add_argument('--unix', help='Force UNIX mode output', action='store_true')
  cli.add_argument('--windows', help='Force Windows mode output', action='store_true')

  cli.add_argument('file', help='YAML file to parse', nargs='*')
  return cli

def load_yaml(text:str|typing.TextIO) -> any:
  '''Utility function

  :param text: YAML document to load
  :returns: structure defined by YAML document

  This is a simple utility function that catches `ParserError`
  exceptions and displays them on-screen.
  '''

  try:
    res = yaml.safe_load(text)
  except yaml.parser.ParserError as err:
    sys.stderr.write(f'Yaml Parser error: {err}\n')
    sys.exit(1)
  return res

def generate_output(outfp:typing.TextIO, res:any, js:int|None) -> None:
  if js is None:
    outfp.write(yaml.dump(res))
  else:
    outfp.write(json.dumps(res, indent = None if js == COMPACT else js))

def main(xargs:list[str]) -> None:
  cli = cmd_cli()
  if '--json' in xargs:
    # I don't know a better way to handle this!
    i = xargs.index('--json')
    xargs[i] = f'--json={COMPACT}'
  args = cli.parse_args(xargs)

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
      generate_output(outfp, res, args.json)
    else:
      for input_file in args.file:
        with open(input_file, 'r') as fp:
          res = load_yaml(fp)
          generate_output(outfp, res, args.json)
  else:
    ypp.init(args.config, args.include, args.define, {}, '')
    if len(args.file) == 0:
      txt = ypp.process(sys.stdin)      
      if not args.json is None:
        res = load_yaml(txt)
        generate_output(outfp, res, args.json)
      else:
        outfp.write(txt)
    else:
      for input_file in args.file:
        txt = ypp.process(input_file)
        if not args.json is None:
          res = load_yaml(txt)
          generate_output(outfp, res, args.json)
        else:
          outfp.write(txt)
  

###################################################################
#
# Main command line
#
###################################################################

if __name__ == '__main__':
  main(sys.argv[1:])
