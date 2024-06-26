#!/usr/bin/env python3
'''Generate SSH keys

'''
import os
import platform

try:
  from cryptography.hazmat.primitives import serialization as crypto_serialization
  from cryptography.hazmat.primitives.asymmetric import rsa
  from cryptography.hazmat.backends import default_backend as crypto_default_backend
except ImportError:
  pass

from ipp import STR, iYamlPreProcessor

DEF_KEYLEN = 4096
'''Default key length'''
PUB = 1
'''Return public keys'''
PRIV = 2
'''Return private keys'''

def ssh_key_gen(keysz: int = DEF_KEYLEN):
  '''Generate a ssh key pair
  :param int keysz: Key size
  :returns str,str: public, private key pair
  '''
  key = rsa.generate_private_key(
      backend=crypto_default_backend(),
      public_exponent=65537,
      key_size=keysz
  )
  private_key = key.private_bytes(
      crypto_serialization.Encoding.PEM,
      crypto_serialization.PrivateFormat.TraditionalOpenSSL,
      crypto_serialization.NoEncryption()
  ).decode('ascii')
  public_key = key.public_key().public_bytes(
      crypto_serialization.Encoding.OpenSSH,
      crypto_serialization.PublicFormat.OpenSSH
  ).decode('ascii')
  return public_key, private_key


def gen(key_store:str, key_id:str, mode:int = PUB, key_sz:int = DEF_KEYLEN, comment:str|None = None):
  '''Return a public/private key pair

  :param str key_store: directory path to keys
  :param str key_id: name of the key
  :param str comment: Key comment (defaults to key_id)
  :param int mode: mode to use, either PRIV or PUB
  :param int key_sz: default key length
  :returns str: key text

  Will generate keys if they do not exist.  Generated keys are stored
  in the key_store directory with name key_id and key_id.pub.
  '''
  if not os.path.isdir(key_store): os.mkdir(key_store)

  base_name = os.path.join(key_store, key_id)
  if mode == PUB and os.path.isfile(base_name + '.pub'):
    # This is a bit of a special case, where public key already
    # exists, and only needs to be returned.
    with open(base_name + '.pub','r') as fp:
      public_key = fp.read().strip()
    return public_key

  if os.path.isfile(base_name) and os.path.isfile(base_name + '.pub'):
    with open(base_name, 'r') as fp:
      private_key = fp.read().strip()
    with open(base_name + '.pub','r') as fp:
      public_key = fp.read().strip()
  else:
    public_key, private_key = ssh_key_gen(key_sz)
    if comment is None: comment = key_id
    public_key = public_key.strip() + " " + comment
    with open(base_name, 'w') as fp:
      fp.write(private_key)
    with open(base_name + '.pub','w') as fp:
      fp.write(public_key)
    if platform.system() != 'Windows':
      # Make sure the key file has the right permissions
      os.chmod(base_name, 0o600)
    print(f'Generated ssh key pair {key_id}')

  if mode == PRIV:
    return private_key
  else:
    return public_key

def macro_sshkey(yppi:iYamlPreProcessor, args:str) -> str:
  '''SSH Key pair generator

  :param yppi: YamlPreProcessor instance
  :param args: additional arguments
  :returns: generated string

  Runs SSHKEY macros and replaces them with the specified key.
  '''
  secret = None
  keytype = PUB
  keylen = DEF_KEYLEN

  for opt in args.split(':'):
    opt = opt.strip()
    if secret is None:
      secret = opt
    elif opt.upper() == 'PUB':
      keytype = PUB
    elif opt.upper() == 'PRIV':
      keytype = PRIV
    elif opt.isdigit():
      keylen = int(opt)
    else:
      yppi.msg(f'Ignoring keygen option {opt}')
  return gen(yppi.lookup(STR.KEY_STORE), secret, keytype, keylen).strip()

def cb_sshkey(yppi:iYamlPreProcessor, args:str, prefix:str = '') -> str:
  '''Handler for SSH key pairs

  :param yppi: Yaml Pre-Processor instance
  :param args: argument string passed in the pre-processor directive
  :param prefix: used to maintain YAML structure
  '''
  key = macro_sshkey(yppi, args)
  prefix2 = prefix.replace('-',' ')
  # Used to handle `- #include` syntax

  txt = ''
  for l in key.split('\n'):
    txt += prefix + l + '\n'
    prefix = prefix2
  return txt

def register(yppi:iYamlPreProcessor) -> None:
  '''Register callback for keypair statements and/or macros

  :param yppi: Yaml Pre-Processor instance
  '''
  yppi.define_var(STR.KEY_STORE, 'keys')
  yppi.register_cb('sshkey', cb_sshkey)
  yppi.register_cb('keygen', cb_sshkey)
  yppi.register_macro('sshkey', macro_sshkey)
  yppi.register_macro('keygen', macro_sshkey)

if __name__ == '__main__':
  import shutil
  pub, priv = ssh_key_gen()
  print('pub', pub)
  print('priv', priv)
  print(gen('keys','linux', PUB, comment='Generated key'))
  print(gen('keys','linux', PUB))
  shutil.rmtree('keys')
