#!/usr/bin/env python3
''' Manage password hashes

This is a module to do password hash manipulations
'''
import os
import random
import string
import yaml

try:
  from passlib.hash import md5_crypt, sha256_crypt, sha512_crypt
except ImportError:
  pass

from d3des import encrypt as d3des
from ipp import STR, iYamlPreProcessor

TEXT = 0
'''Encode password as clear-text'''
MD5 = 1
'''Encode password as an MD5 hash'''
SHA256 = 2
'''Encode password as an SHA256 hash'''
SHA512 = 3
'''Encode password as an SHA512 hash'''
VNC = 4
'''Encode password in a format compatible with `vncpasswd` command'''

DEF_PWLEN = 16
'''Default length for generated passwords'''

HASH_STR = {
  'TEXT': TEXT,
  'MD5': MD5,
  'SHA256': SHA256,
  'SHA512': SHA512,
  'VNC': VNC,
}
'''Text names of supported hashes'''

secrets_cache = {}
'''dict storing cached secrets'''


def gen_rand(length:int = DEF_PWLEN, charset:str|None = None) -> str:
  '''Generate a random string

  :param int length: number of characters to generate
  :param str|None charset: set of characters to use.  If None, it will select lower case, upper case and digits.
  :returns str: random string

  You can use:

  ```python
  import string

  gen_rand(12, string.ascii_lowercase + string.ascii_uppercase + string.digits)
  ```

  ```python
  >>> random.seed(100), gen_rand()
  (None, 'zKFST2OEfWjxnYXa')


  >>> random.seed(101), gen_rand(32)
  (None, 'm8Aa2YG0AL4Nf2utGc21a1CuAxt5RAUg')

  >>> random.seed(102), gen_rand(24,string.digits)
  (None, '737131295684894815597137')

  ```

  '''
  if charset is None or charset == '': charset = string.ascii_lowercase + string.ascii_uppercase + string.digits
  return ''.join(random.sample(charset*length, length))

def enc_passwd(passwd:str, encode:int = TEXT) -> str:
  '''Encode a password using a standard hash

  :param str passwd: password to encode
  :param int encode: hash constant to use
  :returns str: encoded string

  For encode use one of:

  - MD5
  - SHA256
  - SHA512
  - VNC
  - TEXT (the default for all non-recognized hash types)

  ```python
  >>> enc_passwd('onetwo', TEXT)
  'onetwo'

  >>> len(enc_passwd('onetwo', MD5))
  34
  >>> enc_passwd('onetwo', MD5)[:3]
  '$1$'

  >>> len(enc_passwd('onetwo', SHA256))
  63
  >>> enc_passwd('onetwo', SHA256)[:3]
  '$5$'

  >>> len(enc_passwd('onetwo', SHA512))
  106
  >>> enc_passwd('onetwo', SHA512)[:3]
  '$6$'

  >>> enc_passwd('onetwo', VNC)
  '15udw9Bnk/s='

  ```
  '''

  if encode == MD5:
    return md5_crypt.hash(passwd)
  elif encode == SHA256:
    return sha256_crypt.hash(passwd,rounds=5000)
  elif encode == SHA512:
    return sha512_crypt.hash(passwd,rounds=5000)
  elif encode == VNC:
    return d3des(passwd)
  else:
    return passwd


def gen(secrets_file:str, secret:str, encode:int = TEXT, pwlen:int = DEF_PWLEN, charset:str|None = None) -> str:
  '''Password generator

  :param str secrets_file: path to the secrets file store
  :param str secret: secret to use
  :param int encode: constant with hash type to use
  :param int pwlen: password length
  :param str charset: character set (defaults to None)
  :returns str: secret string

  This will either use an existing password or generate a new one.  This
  will update the `secrets_file` if a new password is generated.

  ```python
  >>> len(gen('pwgen.txt','linux', pwlen=32))
  32

  ```
  '''
  if len(secrets_cache) == 0:
    if os.path.isfile(secrets_file):
      with open(secrets_file,'r') as fp:
        secrets = yaml.safe_load(fp)
        if secrets: secrets_cache.update(secrets)

  if secret in secrets_cache:
    passwd = secrets_cache[secret]
  else:
    passwd = gen_rand(pwlen, charset)
    secrets_cache[secret] = passwd
    with open(secrets_file,'w') as fp:
      fp.write(yaml.dump(secrets_cache))
    print(f'Generated password for {secret} as "{passwd}"')

  return enc_passwd(passwd, encode)

def macro_pwgen(yppi:iYamlPreProcessor, args:str) -> str:
  '''Implements pwgen macro

  :param yppi: YamlPreProcessor instance
  :param args: additional arguments
  :returns: generated string

  Runs PWGEN macros and replaces them with the specified password.
  It will either read them from the ``secrets_file`` or will
  create a new password as needed.

  Post-processed line will contain the specified password and this can
  be formatted according to the macro's arguments.
  '''

  secret = None
  encoding = TEXT
  pwlen = DEF_PWLEN
  chrset = ''

  for opt in args.split(':'):
    opt = opt.strip()
    if secret is None:
      secret = opt
    elif opt.upper() in HASH_STR:
      encoding = HASH_STR[opt.upper()]
    elif opt.isdigit():
      pwlen = int(opt)
    elif opt.upper() == 'UPPER':
      chrset += string.ascii_uppercase
    elif opt.upper() == 'LOWER':
      chrset += string.ascii_lowercase
    elif opt.upper() == 'DIGITS':
      chrset += string.digits
    else:
      yppi.msg( f'Ignoring pwgen option {opt}')

  return gen(yppi.lookup(STR.SECRETS_FILE), secret, encoding, pwlen, chrset)

def macro_randstr(yppi:iYamlPreProcessor, args:str) -> str:
  '''Implements randstr macro

  :param yppi: YamlPreProcessor instance
  :param args: additional arguments
  :returns: generated string

  Create a random string
  '''
  rndlen = DEF_PWLEN
  chrset = ''

  for opt in args.split(':'):
    opt = opt.strip()
    if opt.isdigit():
      rndlen = int(opt)
    elif opt.upper() == 'UPPER':
      chrset += string.ascii_uppercase
    elif opt.upper() == 'LOWER':
      chrset += string.ascii_lowercase
    elif opt.upper() == 'DIGITS':
      chrset += string.digits
    else:
      yppi.msg( f'Ignoring rndstr option {opt}')

  return gen_rand(rndlen,chrset)


def register(yppi:iYamlPreProcessor) -> None:
  '''Register callback for pwgen macros

  :param yppi: Yaml Pre-Processor instance
  '''
  yppi.define_var(STR.SECRETS_FILE, 'secrets.yaml')
  yppi.register_macro('pwgen', macro_pwgen)
  yppi.register_macro('rndstr', macro_randstr)


if __name__ == '__main__':
  import doctest
  import sys

  gen('pwgen.txt','linux', pwlen=32)
  failures, tests = doctest.testmod()

  os.unlink('pwgen.txt')

  if failures > 0: sys.exit(1)

