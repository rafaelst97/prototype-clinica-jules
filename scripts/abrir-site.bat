@echo off
start chrome "http://localhost:8080/index.html"
cd /d "%~dp0"
python -m http.server 8080
