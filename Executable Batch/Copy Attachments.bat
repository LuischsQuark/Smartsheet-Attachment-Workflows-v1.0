@echo off
cd /d C:\Users\lchavessolis\Documents\SMAR-Attach-wfls
set API_ACCESS_KEY=my_secure_api_key
start /min cmd /k python copyattachments.py
timeout /t 5
start http://127.0.0.1:5000