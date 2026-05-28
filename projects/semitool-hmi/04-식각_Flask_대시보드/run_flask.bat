@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [etchflask] requirements 설치 중...
python -m pip install -q -r requirements.txt
if errorlevel 1 (
  echo pip 실패. Python 설치 및 PATH를 확인하세요.
  pause
  exit /b 1
)
echo [etchflask] Flask 서버 시작 http://127.0.0.1:5000
python app.py
pause
