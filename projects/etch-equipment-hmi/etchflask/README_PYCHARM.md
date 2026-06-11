# PyCharm에서 Flask 서버 실행하기

> **프로젝트 경로:** `C:\etchflask` (식각 HMI 모니터링 서버)  
> 관련: [README.md](README.md) · [REMOTE_MONITORING.md](REMOTE_MONITORING.md)

## 가장 빠른 실행 (배치 파일)

`C:\etchflask\run_flask.bat` 더블클릭

- `requirements.txt` 설치 후 Flask 시작
- 브라우저에서 `http://127.0.0.1:5000` 접속 (식각 대시보드)

## 설정 방법

### 1. PyCharm 프로젝트 열기
1. PyCharm 실행
2. `File` → `Open` → `C:\etchflask` 폴더 선택

### 2. Python 인터프리터 설정
1. `File` → `Settings` (또는 `Ctrl+Alt+S`)
2. `Project: etchflask` → `Python Interpreter`
3. 가상환경 생성:
   - `Add Interpreter` → `New environment` → `venv` 폴더 선택
   - 또는 기존 가상환경 사용: `Existing environment` → `venv\Scripts\python.exe` 선택

### 3. 패키지 설치
1. PyCharm 하단의 `Terminal` 탭 열기
2. 다음 명령어 실행:
   ```bash
   pip install -r requirements.txt
   ```

### 4. Run Configuration 설정
1. `Run` → `Edit Configurations...`
2. `+` 버튼 클릭 → `Python` 선택
3. 설정:
   - **Name**: `Flask Server`
   - **Script path**: `C:\etchflask\app.py` 파일 선택
   - **Working directory**: `C:\etchflask` 선택
   - **Python interpreter**: 위에서 설정한 인터프리터 선택

### 5. Flask 서버 실행
1. 상단 메뉴에서 `Flask Server` 선택
2. 실행 버튼 클릭 (▶️) 또는 `Shift+F10`
3. 서버가 시작되면 브라우저에서 `http://127.0.0.1:5000` 접속

## 실행 확인

서버가 정상적으로 시작되면 콘솔에 바인드 주소가 표시됩니다. WPF HMI에서 `FlaskBaseUrl`이 동일한지 확인하세요.

## 문제 해결

### 브라우저가 자동으로 열리지 않는 경우
- 수동으로 `http://127.0.0.1:5000` 접속

### 포트가 이미 사용 중인 경우
- `etch_config.py`의 `FLASK_PORT` 변경 또는 5000 포트 사용 프로세스 종료

### 패키지가 설치되지 않은 경우
- `pip install -r requirements.txt` 실행

### WPF HMI와 연결
- WPF `appsettings.json`의 `FlaskBaseUrl` = `http://127.0.0.1:5000` (현장 PC)
- 모니터링 PC: `http://<현장IP>:5000`
