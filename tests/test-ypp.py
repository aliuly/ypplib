#!python3
import hashlib
import os
import re
import shlex
import subprocess
import sys
import yaml

ypplib_dir = os.path.join(os.path.dirname(__file__),'..')
output_txt = 'output.txt'
# ~ sys.path.append(ypplib_dir)
# ~ from ypp import YamlPreProcessor, STR

def remove_passwds(src:str|bytes) -> str|bytes:
  if isinstance(src,bytes):
    text = src.decode()
    text = re.sub(r'(\$[0-9]\$)[a-zA-Z0-9+/.]+\$[a-zA-Z0-9+/.]+','\1___$',text)
    return text.encode()
  else:
    return re.sub(r'(\$[0-9]\$)[a-zA-Z0-9+/.]+\$[a-zA-Z0-9+/.]+','\1___$',src)

def run_ypp(args:str) -> tuple[int,str,str]:
  cmd = './py -m ypp '
  cmd += args
  foutput = os.path.join(ypplib_dir, output_txt)

  if os.path.isfile(foutput): os.unlink(foutput)

  sys.stderr.write(cmd+' : ')
  rc = subprocess.run(cmd,
                      capture_output=True,
                      text=True,
                      shell=True,
                      cwd = ypplib_dir)
  if os.path.isfile(foutput):
    with open(foutput,'rb') as fp:
      result = hashlib.md5(remove_passwds(fp.read()))
      md5 = result.hexdigest()
      sys.stderr.write(f' {md5} ')
    os.unlink(foutput)
  else:
    md5 = None
  sys.stderr.write(f' {rc.returncode}\n')
  return [ args, rc.returncode, remove_passwds(rc.stdout), rc.stderr, md5 ]


cmd_list = [
  '*-h',
  '-Idata/snippets --json data/demo2.yaml',
  '-Idata/snippets data/letest.yaml',
  '-DSID=sys1 -Idata/snippets --json data/letest.yaml',
  'data/xx.yaml',
  '-Idata/snippets -DSID=tsv2 --json data/ts-v2.yaml',
  '-DUSE_ACME -DSID=sys1 -Idata/snippets --json data/letest.yaml',
  '-Idata/snippets -DUSE_ACME -DSID=tsv2 --json data/ts-v2.yaml',
]
modes = [
  '--unix',
  '--windows',
  '',
  None,
]

def generate_output():
  gen = []
  for cmd in cmd_list:
    omode = True
    if cmd[0] == '*':
      omode = False
      cmd = cmd[1:]
    if omode:
      for m in modes:
        if m is None:
          gen.append(run_ypp(f'{cmd}'))
        else:
          gen.append(run_ypp(f'-o {output_txt} {m} {cmd}'))
    else:
      gen.append(run_ypp(cmd))

  return gen

def compare_res(seta, setb):
  if len(seta) != len(setb):
    sys.stderr.write(f'Sets have different number of items len(a)={len(seta)}, len(b)={len(setb)}\n')
    sys.exit(1)
  i = 0
  rc = 0
  while i < len(seta):
    if yaml.dump(seta[i])  != yaml.dump(setb[i]):
      sys.stderr.write(f'Error Test#{i} ')
      if seta[i][0] == setb[i][0]:
        sys.stderr.write(f'"{seta[i][0]}"')
      else:
        sys.stderr.write(f'"{seta[i][0]}"|"{setb[i][0]}"')
      sys.stderr.write(' FAILED\n')
      rc += 1
    i += 1
  sys.exit(0 if rc == 0 else 1)

if __name__ == '__main__':
  if len(sys.argv) == 3 and sys.argv[1] == 'save':
    res = generate_output()
    with open(os.path.join(ypplib_dir,sys.argv[2]), 'w') as fp:
      fp.write(yaml.dump(res))
  elif len(sys.argv) == 3 and sys.argv[1] == 'run':
    with open(os.path.join(ypplib_dir,sys.argv[2]), 'r') as fp:
      saved = yaml.safe_load(fp)
    res = generate_output()
    sys.stderr.write('\n===\n\n')
    compare_res(res, saved)
  else:
    res = generate_output()
    sys.stderr.write('\n===\n\n')
    print(yaml.dump(res))
