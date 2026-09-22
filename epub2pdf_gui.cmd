@echo off
rem  ===========================================================================
rem  epub2pdf_gui.cmd -- launcher for the GUI version (needs NO console input).
rem  Double-click it: a graphical window opens; paste the epub path there
rem  (or click the "choose file" button) and click the convert button.
rem  NOTE: keep this file PURE ASCII -- cmd reads it with the console code page
rem        (936 on Chinese Windows), so any non-ASCII text here can turn into a
rem        garbage command and break parsing.
rem  ===========================================================================
setlocal
set "HERE=%~dp0"
set "PY="
where python  >nul 2>nul && set "PY=python"
if not defined PY where py >nul 2>nul && set "PY=py -3"
if not defined PY goto :nopython

%PY% -c "import weasyprint" >nul 2>nul
if errorlevel 1 goto :nopkg

%PY% -c "import tkinter" >nul 2>nul
if errorlevel 1 goto :notk

where pythonw >nul 2>nul && goto :withpythonw
start "" %PY% "%HERE%epub2pdf_gui.py"
exit /b 0

:withpythonw
start "" pythonw "%HERE%epub2pdf_gui.py"
exit /b 0

:nopython
echo.
echo  [ERROR] Python not found.  Please install Python 3 first.
echo          Download: https://www.python.org/downloads/
echo.
pause
exit /b 1

:nopkg
echo.
echo  [ERROR] weasyprint is not installed for this Python.
echo          Please run:  pip install weasyprint
echo.
pause
exit /b 1

:notk
echo.
echo  [ERROR] This Python has no tkinter (needed for the window).
echo          Re-run the Python installer and tick "tcl/tk and IDLE".
echo.
pause
exit /b 1
