@echo off
cd /d "C:\Users\yokki\x-analytics"
"C:\Users\yokki\AppData\Local\Python\pythoncore-3.14-64\python.exe" -u export_engagement.py
git add data/engagement.csv
git commit -m "Update engagement data %date%"
git push origin main
