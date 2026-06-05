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
echo [etchflask] 식각 Flask ONLY — FarmUI(C:\farmui)와 동시 실행 시 포트 5000 충돌
echo [etchflask] Flask 서버 시작 (현장 PC — 0.0.0.0:5000)
echo   현장 브라우저: http://127.0.0.1:5000
echo   모니터링 PC:   http://^<이 PC LAN IP^>:5000  ^(ipconfig 참고^)
echo   자세한 구성: REMOTE_MONITORING.md
echo   SQLite 이력 영구 저장: set ETCH_USE_DB=1 후 실행 (data\etch_monitoring.db)
python app.py
pause
