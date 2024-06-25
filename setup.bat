@echo off
setlocal
call %~dp0%vars.bat

if "%proxy%"=="" (
  set proxy=
) else (
  echo Using proxy %proxy%
  set proxy=--proxy=%proxy%
)

REM ~ pip install %proxy% --only-binary=netifaces python-openstackclient
REM ~ pip install %proxy% otcextensions
REM ~ pip install %proxy% pyinstaller

pip install %proxy% icecream
pip install %proxy% docutils sphinx myst-parser sphinx-autodoc2 sphinx-argparse
pip install %proxy% --only-binary=cryptography cryptography passlib

