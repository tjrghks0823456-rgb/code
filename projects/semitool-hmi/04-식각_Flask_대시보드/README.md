# 식각 Flask 대시보드

WPF 식각 장비 UI에서 전송하는 센서/장비 상태 데이터를 받아 브라우저 대시보드와 JSON API로 보여주는 Flask 서버입니다.

## 실행

```powershell
pip install -r requirements.txt
python app.py
```

서버 주소는 `http://localhost:5000` 입니다.

## 주요 파일

- `app.py`: Flask 서버와 API 엔드포인트
- `data_manager.py`: 센서 데이터, 식각 이력, 이벤트 메모리 관리
- `etch_ai.py`: AI 상태/예측 스텁
- `templates/etch_dashboard.html`: 웹 대시보드 화면
- `run_flask.bat`: Windows 실행 스크립트

## 제외한 파일

로컬 로그, Python 캐시, IDE 설정, 가상환경 파일은 GitHub 업로드 대상에서 제외했습니다.
