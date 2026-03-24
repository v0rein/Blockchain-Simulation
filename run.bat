@echo off
echo Starting 3 Blockchain Nodes...

start cmd /k "title Node 5000 & cd /d %~dp0 & .venv\Scripts\activate & python server.py -p 5000"
start cmd /k "title Node 5001 & cd /d %~dp0 & .venv\Scripts\activate & python server.py -p 5001"
start cmd /k "title Node 5002 & cd /d %~dp0 & .venv\Scripts\activate & python server.py -p 5002"

echo Nodes are starting in separate windows!
echo Node 1: http://localhost:5000
echo Node 2: http://localhost:5001
echo Node 3: http://localhost:5002
pause
