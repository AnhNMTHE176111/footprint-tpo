@echo off
REM Nhay dup file nay tren may Windows: tu git pull + copy DLL vao Optimus Flow.
REM Muon bo qua git pull: chay "deploy-windows.bat -NoPull"
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0deploy-windows.ps1" %*
