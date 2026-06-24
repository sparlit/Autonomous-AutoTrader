@echo off
REM Phoenix Ascendant - Windows Setup Entry Point
powershell.exe -ExecutionPolicy Bypass -File .\CONFIGURE_AAT.ps1
pause

powershell.exe -ExecutionPolicy Bypass -File .\INSTALL_AAT.ps1
pause

powershell.exe -ExecutionPolicy Bypass -File .\LAUNCH_AAT.ps1
pause

