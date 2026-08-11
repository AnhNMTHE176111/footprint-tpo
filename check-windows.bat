@echo off
REM Nhay dup: KIEM TRA xem DLL ben Optimus Flow co dung ban moi nhat trong repo khong.
REM Khong copy, khong sua gi — chay luc nao cung an toan, ke ca khi Optimus Flow dang mo.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0deploy-windows.ps1" -Verify -NoPull %*
