#!python3
import difflib
import hashlib
import json
import os
import platform
import re
import shlex
import subprocess
import sys
import typing

ypplib_dir = os.path.join(os.path.dirname(__file__),'..')
output_txt = 'output.txt'

def remove_passwds(src:str) -> str:
  return re.sub(r'(\$[0-9]\$)[a-zA-Z0-9+/.]+\$[a-zA-Z0-9+/.]+',r'\1___$_________',src)

def run_ypp(args:str) -> tuple[int,str,str]:
  cmd = 'py -m ypp ' if platform.system() == 'Windows' else './py -m ypp '
  cmd += args

  sys.stderr.write(cmd+' : ')
  outpath = os.path.join(ypplib_dir, output_txt)

  if os.path.isfile(outpath): os.unlink(outpath)
  rc = subprocess.run(cmd,
                      capture_output=True,
                      text=True,
                      shell=True,
                      cwd = ypplib_dir)
  sys.stderr.write(f' {rc.returncode}\n')
  if os.path.isfile(outpath):
    with open(outpath,'rb') as fp:
      hasher = hashlib.md5()
      hasher.update(fp.read())
      md5 = hasher.hexdigest()
    os.unlink(outpath)
  else:
    md5 = None

  return  rc.returncode, remove_passwds(rc.stdout).split('\n'), rc.stderr.split('\n'), md5

def differ(seg:str, a:list[str], b:list[str], fp:typing.TextIO) -> int:
  sa = '\n'.join(a)
  sb = '\n'.join(b)
  if sa == sb: return 0

  fp.write(f'{seg} differs\n')
  diff = difflib.unified_diff(sa.splitlines(keepends=True),
                              sb.splitlines(keepends=True),
                              n=0)
  fp.writelines(diff)
  return 1

def run_cmd(args:list[str]) -> None:
  match args[0]:
    case 'run':
      # Run test case
      yppcmd = shlex.join(args[1:])
      rc, out, err, md5 = run_ypp(yppcmd)
      print(json.dumps({'args': yppcmd, 'rc': rc, 'out': out, 'err': err, 'md5': md5}, indent=4))
    case 'test':
      diff = 0
      for testcase in args[1:]:
        with open(testcase) as fp:
          jsdat = json.load(fp)
        if not 'md5' in jsdat: jsdat['md5'] = None

        rc, out, err, md5 = run_ypp(jsdat['args'])

        if rc != jsdat['rc']:
          diff += 1
          sys.stderr.write(f'Return code was {rc}.  Expected {jsdat['rc']}\n')
        diff += differ('out', out, jsdat['out'], sys.stderr)
        diff += differ('err', err, jsdat['err'], sys.stderr)
        if (str(md5) != str(jsdat['md5'])):
          diff += 1
          sys.stderr.write(f'MD5 was {md5}.  Expected {jsdat['md5']}\n')
      sys.exit(0 if diff == 0 else 1)
    case _:
      print(args)


if __name__ == '__main__':
  run_cmd(sys.argv[1:])
  # py -m ypp -Idata/snippets -Dsecrets_file=tests/data.yaml -Dkey_store=tests/data --json=2 data/demo2.yaml :  0
