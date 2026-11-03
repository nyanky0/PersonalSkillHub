@echo off
REM Windows wrapper for Lightpanda executing in WSL2 Ubuntu
wsl.exe -d Ubuntu -- bash -lic "export PATH=\"$HOME/.local/bin:$PATH\" && lightpanda %*"
