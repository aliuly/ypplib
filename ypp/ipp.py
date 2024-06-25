#!/usr/bin/env python3
''' YAML pre-processor interface

'''
import sys
import typing

try:
  from icecream import ic
  ic.configureOutput(includeContext=True) # Optional... shows source and line numbers
except ImportError:  # Graceful fallback if IceCream isn't installed.
  ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa


class iYamlPreProcessor:
  '''This class defines the interface for YamlPreProcessor
  '''
  def __init__(self) -> None:
    '''Initialize pre-processor interface
    '''
    self.filename = None
    self.line = 0

  def save_state(self, filename:str, line:int = 0) -> tuple[str,int]:
    saved_name = self.filename
    saved_line = self.line
    self.filename = filename
    self.line = line
    return saved_name, saved_line
  
  def restore_state(self, state:tuple[str,int]) -> None:
    self.filename, self.line = state
    
  def get_filename(self) -> str:
    return self.filename

  def msg(self, text:str) -> None:
    if self.filename:
      sys.stderr.write(f'"{self.filename}",{self.line}: {text}\n')
    else:
      sys.stderr.write(f'<None>,{self.line}: {text}\n')
  
  def process(self, inpfile:str|typing.TextIO, prefix:str = '') -> str:
    if isinstance(inpfile,str):
      return self.read_file(inpfile, prefix)
    else:
      state = self.save_state(None)
      txt = self.parser(inpfile, prefix)
      self.restore_state(state)
      return txt

  # These methods should be implemented in child classes
  def parser(self, filep:typing.TextIO, prefix:str = '') -> str:
    raise NotImplementedError
  def read_file(self, filename:str, prefix:str = '') -> str:
    raise NotImplementedError    
  def expand_vars(self, line:str, loopctl:dict = dict()) -> str:
    raise NotImplementedError
  def vexists(self, name:str) -> bool:
    raise NotImplementedError
  def lookup(self, name:str, loopctl:dict = dict()) -> str|None:
    raise NotImplementedError
  def define_var(self, key:str, value:str, var_expand = False) -> None:
    raise NotImplementedError
  def register(self, directive:str, callback:typing.Callable, expand_vars:bool = True, ex_data:any = None) -> None:
    raise NotImplementedError
  def find_include(self, fname:str) -> str:
    raise NotImplementedError
  def secrets_file(self) -> str:
    raise NotImplementedError
  def key_store(self) -> str:
    raise NotImplementedError
