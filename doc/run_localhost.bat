@echo off
cd ../docs/en
start python -m http.server
start http://localhost:8000/