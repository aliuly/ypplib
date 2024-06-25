@echo off

if NOT "%PKGVER%" == "" goto :DONE

  rem Desired Python version...
  rem https://github.com/winpython/winpython/releases/tag/7.5.20240410final
  rem Tested with 3.12
  rem
  set PKGVER=64-31230
  rem
  rem Install to possible locations:
  rem
  rem %USERPROFILE%\WPy%PKGVER%
  rem %~dp0%\WPy%PKGVER%
  rem

  set ENVBAT=scripts\env.bat
  set SDIR=%~dp0

  if NOT EXIST %USERPROFILE%\WPy%PKGVER%\%ENVBAT% goto :ls1p3
    set WPYDIR=%USERPROFILE%\WPy%PKGVER%
    goto :ls1end
  :ls1p3
  if NOT EXIST %SDIR%WPy%PKGVER%\%ENVBAT% goto :ls1p4
    set WPYDIR=%SDIR%WPy%PKGVER%
    goto :ls1end
  :ls1p4
    echo No Suitable WinPython Installation found
    set PKGVER=
    goto :DONE
  :ls1end

  REM Note, this modifies HOME variable to %WPYDIR%\settings
  call %WPYDIR%\%ENVBAT%
:DONE

set proxy=10.41.5.36:8080
REM Requires authentication
REM ~ set proxy=sia-lb.telekom.de:8080
REM ~ set http_proxy=http://%proxy%/
REM ~ set https_proxy=http://%proxy%/
REM ~ set proxy=
REM ~ set http_proxy=
REM ~ set https_proxy=
REM ~ set MYOTC_OPTS=-A

set ENVBAT=
set SDIR=
