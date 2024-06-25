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

pip install %proxy% --requirement %~dp0%requirements.txt
REM ~ icecream
REM ~ pip install %proxy% docutils sphinx myst-parser sphinx-autodoc2 sphinx-argparse
REM ~ pip install %proxy% --only-binary=cryptography cryptography passlib

