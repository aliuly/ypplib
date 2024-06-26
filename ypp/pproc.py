#!/usr/bin/env python3
'''Main YAML pre-processor implementation

This can be used as python module or as a command line.

If used on the command line, it acts as a pre-processor reading
YAML files with pre-processor directives, and outputs
the processed file.

Optionally it can parse the generated YAML and dump it as a JSON
object (which is also valid YAML document)
'''

import os
import re
import sys
import typing

import cfgfile
import extcmd
import includes
import pwhash
import sshkeys

from ipp import STR, iYamlPreProcessor

try:
  from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
  ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

class MK:
  '''Characters used to signal macros'''
  SIGNAL = '$'
  '''Macro character indicator'''
  OPEN = '<'
  '''Open macro character'''
  CLOSE = '>'
  '''Close macro character'''

class YppDirective:
  '''Class used to manage pre-processor directive or macro callbacks'''
  def __init__(self, callback:typing.Callable, expand_vars:bool = True):
    '''YppDirective constructor
    :param callback: Function to call to hanlde this macro or directive
    :param expand_vars: If True (default) args have variables expanded.  If `False`, variable expansion is skipped.
    '''
    self.callback = callback
    self.expand_vars = expand_vars

def __TODO__(yppi:iYamlPreProcessor, args:str, prefix:str = '') -> str:
  ''' _internal_ Place holder for un-implemented directive/macros

  :meta internal:
  :param yppi: Yaml Pre-Processor instance
  :param args: argument string passed in the pre-processor directive
  :param prefix: used to maintain YAML structure (ignored for macros)
  :returns: processed output
  '''
  raise NotImplementedError

class YamlPreProcessor(iYamlPreProcessor):
  '''YAML Pre-processor instance'''
  # Complied RegExps
  RE_VALID_ID = re.compile(r'^[_A-Za-z][_A-Za-z0-9]*$')
  ''' Regular expressions to validate pre-processor variable names '''
  RE_PP_DIRECTIVE = re.compile(r'^(\s*)#\s*([a-z]+)\s*')
  ''' Regular expression to get pre-processor directives '''
  RE_PP_DIRECTIVE_ALT = re.compile(r'^(\s*-\s*)#\s*([a-z]+)\s*')
  ''' Regular expression to get alternative pre-processor directives '''

  RE_DEFER = re.compile(r'^\s*--(defer)\s+')
  ''' Regular expression to check if variable expansion should be deferred '''
  RE_DEFINE = re.compile(r'^([_A-Za-z][_A-Za-z0-9]*)\s*')
  ''' Regular expression to parse definitions '''

  def cb_define(yppi:iYamlPreProcessor, args:str, prefix:str = '') -> str:
    '''_internal_ Helper function to define variables
    :meta internal:
    :param yppi: Yaml Pre-Processor instance
    :param args: argument string passed in the pre-processor directive
    :param prefix: used to maintain YAML structure (ignored for macros)
    :returns: processed output
    '''
    return YamlPreProcessor.cb_do_define(yppi, args, False)
  def cb_default(yppi:iYamlPreProcessor, args:str, prefix:str = '') -> str:
    '''_internal_ Helper function to default variables
    :meta internal:
    :param yppi: Yaml Pre-Processor instance
    :param args: argument string passed in the pre-processor directive
    :param prefix: used to maintain YAML structure (ignored for macros)
    :returns: processed output
    '''
    return YamlPreProcessor.cb_do_define(yppi, args, True)
  def cb_do_define(yppi:iYamlPreProcessor, args:str, as_default:bool = False) -> str:
    '''_internal_ Helper function to handle define/default statements
    :meta internal:
    :param yppi: Yaml Pre-Processor instance
    :param args: argument string passed in the pre-processor directive
    :param prefix: used to maintain YAML structure (ignored for macros)
    :returns: processed output
    '''
    mv = YamlPreProcessor.RE_DEFINE.match(args)
    if not mv:
      yppi.msg('Invalid define/default directive')
      return ''

    vname = mv.group(1)
    args = args[mv.end():]
    if as_default and yppi.vexists(vname): return ''

    mv = YamlPreProcessor.RE_DEFER.match(args)
    if mv:
      args = args[mv.end():]
      expand_vars = False
    else:
      expand_vars = True
    # ~ ic(vname,args,expand_vars)
    yppi.define_var(vname, args, expand_vars)
    return ''

  def define_var(self, key:str, value:str, var_expand = False) -> None:
    '''Define a pre-processor variable
    :param key: name of variable to define
    :param value: value to assign to variable
    :param var_expand: if `True` the string in `value` will be evalued for variable expansion.  `False` omits variable expansion (This is the default).
    '''
    if not YamlPreProcessor.RE_VALID_ID.match(key):
      self.msg(f'Invalid keyname "{key}')
      return
    if var_expand: value = self.expand_vars(value)
    self.ppv[key] = value

  def register_cb(self, directive:str, callback:typing.Callable, expand_vars:bool = True) -> None:
    '''Register a pre-processor directive callback
    :param directive: directive to register
    :param callback: Function to call when executing this pre-processor directive
    :param expand_vars: If `True` passed arguments will be check for variable expansions before calling function.  `False` variable expansions can be omitted.
    '''
    self.cmds[directive] = YppDirective(callback, expand_vars)
  def register_macro(self, macro:str, callback:typing.Callable, expand_vars:bool = True) -> None:
    '''Register a macro callback
    :param macro: macro to register
    :param callback: Function to call when executing this macro
    :param expand_vars: If `True` passed arguments will be check for variable expansions before calling function.  `False` variable expansions can be omitted.
    '''
    self.macros[macro] = YppDirective(callback, expand_vars)

  def cb_error(yppi:iYamlPreProcessor, args:str, prefix:str = '') -> str:
    '''Abort program execution
    :param yppi: Yaml Pre-Processor instance
    :param args: message to display
    :param prefix: ignored
    '''
    yppi.msg(args)
    sys.exit(1)
    return ''

  def cb_warn(yppi:iYamlPreProcessor, args:str, prefix:str = '') -> str:
    '''Display warning on stderr
    :param yppi: Yaml Pre-Processor instance
    :param args: message to display
    :param prefix: ignored
    '''
    yppi.msg(args)
    return ''

  def __init__(self, config:list[str] = [], include:list[str] = [], define:list[str] = [], app_defaults:dict[str] = {}, env_prefix:str = ''):
    '''Initialize pre-processor data

    :param config: List of config yaml files to read
    :param include; list of directories to add to include path
    :param define: list of key value pairs to define
    :param app_defaults: dictionary with application defaults
    :param env_prefix: Read variables for variable starting with env_prefix

    - defaults from application
    - read defaults from config yaml
    - read defaults from environment
    - from command line arguments: -D -I
    - in-line defines
    '''
    super().__init__()

    self.cmds = {
      'define': YppDirective(YamlPreProcessor.cb_define, False),
      'default': YppDirective(YamlPreProcessor.cb_default, False),
      'include': YppDirective(includes.cb_inc),
      'exec': YppDirective(extcmd.cb_exec),
      'error': YppDirective(YamlPreProcessor.cb_error),
      'warn': YppDirective(YamlPreProcessor.cb_warn),
      'cfgload': YppDirective(cfgfile.cb_load),
    }
    self.macros = {
      'sshkey': YppDirective(sshkeys.macro_sshkey),
      'keygen': YppDirective(sshkeys.macro_sshkey),
    }
    self.ppv = {
      STR.INCLUDE_PATH: '',
    }

    sshkeys.register(self)
    pwhash.register(self)

    self.ppv.update(app_defaults)

    # Read configuration files (formatted as YAML)
    for cfg_file in config:
      cfgfile.load(cfg_file, self)

    # Initialize from environment variables
    prefix_len = len(env_prefix)
    for key,val in os.environ.items():
      if key.startswith(env_prefix):
        self.ppv[key[prefix_len:]] = val
    del prefix_len

    # Update include path
    if not STR.INCLUDE_PATH in self.ppv: self.ppv[STR.INCLUDE_PATH] = ''
    cc = '' if self.ppv[STR.INCLUDE_PATH] == '' else STR.PATH_SEPARATOR
    for incdir in include:
      if not os.path.isdir(incdir): continue
      self.ppv[STR.INCLUDE_PATH] += cc + incdir
      cc = STR.PATH_SEPARATOR

    # Handle define cli options
    for kvp in define:
      if '=' in kvp:
        kvp = kvp.split('=',1)
        key = kvp[0]
        val = kvp[1]
      else:
        key = kvp
        val = ''
      if YamlPreProcessor.RE_VALID_ID.match(key):
        self.ppv[key] = val
      else:
        self.msg(f'{key} is not a valid name')

  def secrets_file(self) -> str:
    '''Return the value of `secrets_file`'''
    return self.ppv[STR.SECRETS_FILE]
  def key_store(self) -> str:
    '''Return the value of `key_store`'''
    return self.ppv[STR.KEY_STORE]

  def parse_line(line:str) -> tuple[str,str,str]:
    '''_internal_ utility function to parse pre-processor directives
    :meta internal:
    :param line: text to parse
    :returns: tuple(token, args, prefix)
    '''
    mv = YamlPreProcessor.RE_PP_DIRECTIVE.match(line)
    if mv:
      return mv.group(2), line[mv.end():].strip(), mv.group(1)
    mv = YamlPreProcessor.RE_PP_DIRECTIVE_ALT.match(line)
    if mv:
      return mv.group(2), line[mv.end():].strip(), mv.group(1)
    return '','',''

  def parser(self, fp:typing.TextIO, prefix='') -> str:
    '''Process data from a file pointer
    :param typing.TextIO fp: file pointer
    :param str prefix: (optional) Prefix string to maintain YAML structure
    :returns str: processed text

    This is the main YAML pre-processor functions.  Implements most of the
    logic related to YAML pre-processing.

    It takes a file pointer as input, executes the pre-processing statements
    and returns the results as a text string.

    '''
    txt = ''
    cond_stack = []
    prefix2 = prefix.replace('-',' ')
    # Used to handle `- #include` syntax

    for line in fp:
      self.line += 1

      if line.endswith("\n"): line = line[:-1]
      if line.endswith("\r"): line = line[:-1]

      token, args, in_prefix = YamlPreProcessor.parse_line(line)
      match token:
        #
        # Control statements
        #
        case 'else':
          if len(cond_stack):
            cond_stack[0] = not cond_stack[0]
          else:
            self.msg('dangling #else directive')
        case 'endif':
          if len(cond_stack):
            cond_stack = cond_stack[1:]
          else:
            self.msg('dangling #endif directive')
        case 'ifdef':
          if len(cond_stack) > 0 and not cond_stack[0]:
            # suppressing output...
            cond_stack.insert(0,False)
          else:
            if not args:
              self.msg('Missing conditional')
            else:
              if args in self.ppv:
                cond_stack.insert(0,True)
              else:
                cond_stack.insert(0,False)
        case 'ifndef':
          if len(cond_stack) > 0 and not cond_stack[0]:
            # suppressing output...
            cond_stack.insert(0,False)
          else:
            if not args:
              self.msg('Missing conditional')
            else:
              if args in self.ppv:
                cond_stack.insert(0,False)
              else:
                cond_stack.insert(0,True)
        case _:
          #
          # Pre-processor directives
          #
          if len(cond_stack) > 0 and not cond_stack[0]: continue # Suppresing output

          if token in self.cmds:
            if self.cmds[token].expand_vars: args = self.expand_vars(args)
            addme = self.cmds[token].callback(self, args, prefix + in_prefix)
          else:
            addme = prefix + self.expand_vars(line) + '\n'
          txt += addme
          if addme != '':  prefix = prefix2

    return txt

  def read_file(self, filename:str, prefix:str = '') -> str:
    '''Process a file

    :param str filename: filename to read
    :param str prefix: (optional) Prefix string to maintain YAML structure
    :returns str: processed text
    '''

    filename = self.find_include(filename)
    with open(filename, 'r') as fp:
      state = self.save_state(filename)
      txt = self.parser(fp, prefix)
      self.restore_state(state)
    return txt

  def find_include(self, fname:str) -> str:
    ''' Find included file path

    :param str fname: Filename to include
    :returns str: Resolved included file

    First it tries to file as a relative to the current (prev) file.
    If not found, search for it in the Include path.
    '''
    if fname[0] == '/':
      # This is an absolute path!
      return fname

    prev = self.filename
    incpath = self.ppv[STR.INCLUDE_PATH]

    if prev:
      dn = os.path.dirname(prev)
      if dn == '':
        tname = fname
      else:
        tname = os.path.join(dn, fname)
      if os.path.isfile(tname): return tname

    for dn in incpath.split(STR.PATH_SEPARATOR):
      tname = os.path.join(dn,fname)
      if os.path.isfile(tname): return tname

    # Otherwise just hope for the best!
    return fname

  def find_closing_bracket(line:str, off:int) -> int:
    '''Find closing bracket

    :param str line: string to scan
    :param int off: offset in string
    :returns int: returns the index to the closing bracket or -1 if not found

    Used to find the closing bracket for a `$(macro reference)`.  It
    will handle `$$` escapes and nested macro references.

    '''
    i = off
    ln = len(line)
    nesting = 0

    while i < ln:
      if line[i] == MK.SIGNAL and i+1 < ln and line[i+1] == MK.SIGNAL:
        i += 2
        continue
      if line[i] == MK.SIGNAL and i+1 < ln and line[i+1] == MK.OPEN:
        i += 2
        nesting += 1
        continue
      if line[i] == MK.CLOSE:
        if nesting == 0: return i
        nesting -= 1
      i += 1
    return -1

  def vexists(self, name:str) -> bool:
    '''Check if a name exists
    :param name: pre-processor variable to check
    :returns: `True` if `name` exists, `False` otherwise.
    '''
    return True if name in self.ppv else False

  def lookup(self, name:str, loopctl:dict = dict()) -> str|None:
    '''Look-up variable defintions

    :param name: variable to look-up
    :param loopctl: used to catch reference loops
    :returns: expanded string
    '''
    if not name in self.ppv: return None
    if not name in loopctl:
      loopctl[name] = None # Used to prevent loops
      loopctl[name] = self.expand_vars(self.ppv[name],loopctl)
    if loopctl[name] is None:
      self.msg(f'Potential loop in defining "{name}"')
      return f'$({name})'
    return loopctl[name]

  def expand_vars(self, line:str, loopctl:dict = dict()) -> str:
    '''Expand variables

    :param line: text with variables to expand
    :param  loopctl: used to catch reference loops

    Given a string with macro references it will expand them
    '''
    if not MK.SIGNAL in line: return line # This is the trivial case...

    offset = 0
    txt = ''
    lenline= len(line)

    while (pos := line.find(MK.SIGNAL, offset)) != -1:
      txt += line[offset:pos]
      offset = pos
      if pos+1 == lenline: break
      if line[pos+1] == MK.SIGNAL:
        txt += MK.SIGNAL
        offset += 2
        continue
      if line[pos+1] != MK.OPEN:
        txt += line[offset:offset+2]
        offset += 2
        continue

      closing = YamlPreProcessor.find_closing_bracket(line, offset+2)
      if closing == -1: break

      ref = line[offset+2:closing]
      exp = self.run_macro(ref, loopctl)
      if exp is None:
        self.msg(f'Unknown macro "{ref}"')
        txt += line[offset:closing+1]
      else:
        txt += exp

      offset = closing +1
    txt += line[offset:]

    return txt

  def run_macro(self, macro:str, loopctl:dict) -> str|None:
    '''Run macro references

    :param macro: Macro specification to run
    :param loopctl: used to catch reference loops
    :returns: expanded string

    It will run the given macro.  Primarily it is meant to handle
    variable expansions, but it can also handle macros such as:

    - pwgen
    - ssh keygen
    '''
    if ':' in macro:
      macro,args = macro.split(':',1)
    else:
      args = ''

    if macro in self.macros:
      if self.macros[macro].expand_vars: args = self.expand_vars(args)
      return self.macros[macro].callback(self, args)
    elif macro in self.ppv:
      return self.lookup(macro, loopctl)
    else:
      return None

###################################################################
#
# Main command line
#
###################################################################

if __name__ == '__main__':

  # ~ ppv = dict(os.environ)
  # ~ ppv[STR_FILENAME] = None
  # ~ ppv[STR_LINE] = 0
  # ~ ppv['recurse'] = 'windir=$(WINDIR) user=$(USERNAME)'
  # ~ ppv['loop'] = 'infinte $(loop)'

  # ~ ic(ppv)
  # ~ line = '$(recurse) o$$ $(broken) windir=$(WINDIR) $(variable $(nested)) USERNAME=$(USERNAME) line $(inc'
  # ~ ic('Input', line)
  # ~ print(expand_vars(line, ppv))

  # ~ line = 'Infinite $(loop)'
  # ~ ic('Input', line)
  # ~ print(expand_vars(line, ppv))

  pass
