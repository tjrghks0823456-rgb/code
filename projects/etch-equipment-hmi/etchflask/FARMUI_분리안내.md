# FarmUI와 Etch Flask 분리

**같은 포트(5000)를 쓸 수 있지만, 서로 다른 프로그램입니다. 동시에 실행하면 충돌합니다.**

| 프로젝트 | 로컬 경로 | 용도 | 실행 |
|----------|-----------|------|------|
| **Etch Flask** (이 저장소) | `C:\etchflask` | 식각 HMI 원격 모니터링·AI | `run_flask.bat` |
| **FarmUI** (스마트팜) | `C:\farmui\farmui` | 농장·작물 모니터링 | FarmUI 전용 `run_farmui.bat` |

## 이 저장소(etchflask)에 포함되지 않는 것

- FarmUI `crop_config`, 작물 대시보드 `index.html`
- Farm 전용 `ai_analysis.py` / `ml_trainer.py` (삭제됨)
- `run_farmui.bat` (삭제됨 — FarmUI는 `C:\farmui`에서 실행)

## GitHub 저장소 이름

현재 remote가 `yaong832/farmui`로 남아 있을 수 있습니다. **내용은 Etch 전용**이므로 GitHub에서 저장소 이름을 `etchflask`로 바꾸는 것을 권장합니다.

```bash
# GitHub 웹: Settings → Repository name → etchflask
git remote set-url origin https://github.com/yaong832/etchflask.git
```

FarmUI 레거시 이력은 Git 태그/브랜치 `legacy/farm` (커밋 `800ce19` 이전)에서 확인할 수 있습니다.

## WPF 연동

- 클라이언트: `D:\WPFProject\etch_ui` (`yaong832/etch_ui`)
- 설정: `appsettings.json` → `FlaskBaseUrl` = `http://127.0.0.1:5000`
