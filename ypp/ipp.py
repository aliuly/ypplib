#!/usr/bin/env python3
''' YAML pre-processor interface

'''
import platform
import sys
import typing

try:
  from icecream import ic
  ic.configureOutput(includeContext=True) # Optional... shows source and line numbers
except ImportError:  # Graceful fallback if IceCream isn't installed.
  ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

class STR:
  '''String definitions'''
  INCLUDE_PATH = 'include_path'
  '''Include path variable'''
  PATH_SEPARATOR = ';' if platform.system() == 'Windows' else ':'
  '''Path separator character. `:` unless Windows which uses `;`'''
  SECRETS_FILE = 'secrets_file'
  '''Variable containing the filename used to store pwgen secrets'''
  KEY_STORE = 'key_store'
  '''Variable containing the directory used to store generated ssh keys'''

class iYamlPreProcessor:
  '''This class defines the interface for YamlPreProcessor
  '''
  def __init__(self) -> None:
    '''Initialize pre-processor interface
    '''
    self.filename = None
    self.line = 0

  def save_state(self, filename:str, line:int = 0) -> tuple[str,int]:
    '''Save state
    :param filename: Filename being open
    :param line: (optional) start line numbering at `line`
    :returns: state tuple

    Current opened filename and line are returned as a `tuple`
    so the state can be saved in the current called context.

    The current filename and (optionally)line number are set
    to the passed values.

    :Example:

    ```python
    >>> iYamlPreProcessor().save_state('one')
    (None, 0)

    ```
    '''
    saved_name = self.filename
    saved_line = self.line
    self.filename = filename
    self.line = line
    return saved_name, saved_line

  def restore_state(self, state:tuple[str,int]) -> None:
    '''Restore state
    :param state: tuple containing a saved state

    Restore the saved state as returned from the `save_state`
    method.

    '''
    self.filename, self.line = state

  def get_filename(self) -> str:
    '''Returns the current working filename

    :Example:
    ```python
    >>> iYamlPreProcessor().get_filename() is None
    True

    ```

    '''
    return self.filename

  def msg(self, text:str) -> None:
    '''Display an error message on-screen
    :param text: message to print

    Displays a message.  It uses the current state to report
    what `filename` and `line` number is being processed.

    '''
    if self.filename:
      sys.stderr.write(f'"{self.filename}",{self.line}: {text}\n')
    else:
      sys.stderr.write(f'<None>,{self.line}: {text}\n')

  def process(self, inpfile:str|typing.TextIO, prefix:str = '') -> str:
    '''Main entry point for processing YAML documents
    :param inpfile: YAML document to process as either a string containing a filename or a file pointer as returned by `open`
    :param prefix: Prefix used to maintain YAML file structure
    :returns: pre-processed text
    '''
    if isinstance(inpfile,str):
      return self.read_file(inpfile, prefix)
    else:
      state = self.save_state(None)
      txt = self.parser(inpfile, prefix)
      self.restore_state(state)
      return txt

  # These methods should be implemented in child classes
  def parser(self, filep:typing.TextIO, prefix:str = '') -> str:
    '''Entry point for processing file pointers as returned by `open`
    :param filep: File pointer as returned by `open`
    :param prefix: Prefix used to maintain YAML file structure.
    :returns: pre-processed text
    '''
    raise NotImplementedError
  def read_file(self, filename:str, prefix:str = '') -> str:
    '''Entry point for processing files
    :param filename: Name of YAML document file
    :param prefix: Prefix used to maintain YAML file structure.
    :returns: pre-processed text
    '''
    raise NotImplementedError
  def expand_vars(self, line:str, loopctl:dict = dict()) -> str:
    '''Entry point for variable expansion
    :param line: text containing references to expand
    :param loopctl: Internal variable used for loop prevention
    :returns: string with expanded variables
    '''
    raise NotImplementedError
  def vexists(self, name:str) -> bool:
    '''Check if a name exists
    :param name: pre-processor variable to check
    :returns: `True` if `name` exists, `False` otherwise.
    '''
    raise NotImplementedError
  def lookup(self, name:str, loopctl:dict = dict()) -> str|None:
    '''Lookup a pre-processor variable
    :param name: pre-processor variable to look-up
    :param loopctl: Internal variable used for loop control
    :returns: contents of `name` variable, `None` if `name` does not exist.
    '''
    raise NotImplementedError
  def define_var(self, key:str, value:str, var_expand = False) -> None:
    '''Define a pre-processor variable
    :param key: name of variable to define
    :param value: value to assign to variable
    :param var_expand: if `True` the string in `value` will be evalued for variable expansion.  `False` omits variable expansion (This is the default).
    '''
    raise NotImplementedError
  def register_cb(self, directive:str, callback:typing.Callable, expand_vars:bool = True) -> None:
    '''Register a pre-processor directive callback
    :param directive: directive to register
    :param callback: Function to call when executing this pre-processor directive
    :param expand_vars: If `True` passed arguments will be check for variable expansions before calling function.  `False` variable expansions can be omitted.
    '''
    raise NotImplementedError
  def register_macro(self, macro:str, callback:typing.Callable, expand_vars:bool = True, ex_data:any = None) -> None:
    '''Register a macro callback
    :param macro: macro to register
    :param callback: Function to call when executing this macro
    :param expand_vars: If `True` passed arguments will be check for variable expansions before calling function.  `False` variable expansions can be omitted.
    '''
    raise NotImplementedError
  def find_include(self, fname:str) -> str:
    '''Used to find `fname` in the include path
    :param fname: File name to look for
    :returns: translated file path
    Check for `fname` either as an absolute path, otherwise if it
    is relative to the current file being processed.  Lastly it
    will check in the directories as defined in the `include_path`.
    '''
    raise NotImplementedError

if __name__ == '__main__':
  import doctest
  failures, tests = doctest.testmod()
  if failures > 0: sys.exit(1)
