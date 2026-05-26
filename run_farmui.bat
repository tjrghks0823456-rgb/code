@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [farmui] requirements 설치 중...
python -m pip install -q -r requirements.txt
if errorlevel 1 (
  echo pip 실패. Python 설치 및 PATH를 확인하세요.
  pause
  exit /b 1
)
echo.
echo [farmui] Flask 서버 시작 (0.0.0.0:5000)
echo   브라우저: http://127.0.0.1:5000  ^(app.py에서 자동으로 열림^)
echo   같은 PC에서 farm WinForm/WPF가 POST하면 센서 데이터가 표시됩니다.
echo   etchflask와 동시 실행 시 포트 5000 충돌 — 한쪽만 실행하세요.
echo.
python app.py
pause
