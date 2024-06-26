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

pip install %proxy% --requirement %~dp0%requirements.txt

REM these dependancies are Windows specific
pip install %proxy% pyinstaller
