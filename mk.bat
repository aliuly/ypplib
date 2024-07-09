@echo off
setlocal
rd/s/q %~dp0%build
rd/s/q %~dp0%dist
del *.spec
set build=%~dp0%scripts\build.bat

set VENV=%~dp0.venv
call %VENV%\Scripts\activate.bat

call %build% -1 ypp\__main__.py --name ypp -p ypp -p .
dir dist
dist\ypp -h

