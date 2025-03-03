@echo off
cd /d C:\Users\lchavessolis\Documents\SMAR-Attach-wfls\Smartsheet-Attachment-Workflos\Attachment-Move
start /min cmd /k python moveattachments.py
timeout /t 5
start http://127.0.0.1:5000