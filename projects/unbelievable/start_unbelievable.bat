@echo off
title 언블리버블 원클릭 통합 실행기
echo ===================================================
echo   언블리버블 (SH.SON_UNBELIEVABLE) 원클릭 구동기
echo ===================================================
echo.

:: %~dp0 은 현재 실행된 배치 파일의 위치(루트 폴더)를 가리키는 윈도우 내장 마법의 변수입니다.
:: 이를 사용하면 복잡한 경로를 직접 입력하지 않아 한글 인코딩 깨짐 버그가 100% 방지됩니다.

echo 1. 백엔드 (FastAPI) 서버를 새 창에서 실행합니다...
start "Unbelievable Backend (FastAPI)" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate && python -m uvicorn app.main:app --reload --port 8000"

echo 2. 프론트엔드 (Next.js) 서버를 새 창에서 실행합니다...
start "Unbelievable Frontend (Next.js)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo 3. 4초 동안 서버 준비를 대기한 후 브라우저를 자동으로 엽니다...
timeout /t 4 /nobreak >nul
start http://localhost:3000

echo.
echo 통합 가동 프로세스가 완료되었습니다.
echo 켜진 두 개의 백엔드/프론트엔드 검은색 콘솔 창을 유지해 주세요!
echo.
timeout /t 3 >nul
exit
