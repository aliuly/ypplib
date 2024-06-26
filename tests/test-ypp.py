#!python3
import hashlib
import os
import re
import shlex
import subprocess
import sys
import yaml

ypplib_dir = os.path.join(os.path.dirname(__file__),'..')

def remove_passwds(src:str) -> str:
  return re.sub(r'(\$[0-9]\$)[a-zA-Z0-9+/.]+\$[a-zA-Z0-9+/.]+','\1___$',src)

def run_ypp(args:str) -> tuple[int,str,str]:
  cmd = './py -m ypp '
  cmd += args


  sys.stderr.write(cmd+' : ')
  rc = subprocess.run(cmd,
                      capture_output=True,
                      text=True,
                      shell=True,
                      cwd = ypplib_dir)
  sys.stderr.write(f' {rc.returncode}\n')

  return [ args, rc.returncode, remove_passwds(rc.stdout).split('\n'), rc.stderr.split('\n') ]


cmd_list = [
  '-h',
  '-Idata/snippets --json data/demo2.yaml',
  '-Idata/snippets data/letest.yaml',
  '-DSID=sys1 -Idata/snippets --json data/letest.yaml',
  'data/xx.yaml',
  '-Idata/snippets -DSID=tsv2 --json data/ts-v2.yaml',
  '-DUSE_ACME -DSID=sys1 -Idata/snippets --json data/letest.yaml',
  '-Idata/snippets -DUSE_ACME -DSID=tsv2 --json data/ts-v2.yaml',
]

def generate_output():
  gen = []
  for cmd in cmd_list:
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
