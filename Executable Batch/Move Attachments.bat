@echo off
cd /d C:\Users\lchavessolis\Documents\SMAR-Attach-wfls
start /min cmd /k python moveattachments.py
timeout /t 5
start http://127.0.0.1:5000