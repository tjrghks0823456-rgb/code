# GitHub 저장소 분류표

> 목표 직무: **C# / WPF 기반 반도체·디스플레이 장비 PC 제어 소프트웨어 개발자**  
> 이 문서는 포트폴리오 정리 기준에 따라 각 저장소/폴더를 분류한 기록입니다.

---

## 분류 기준

| 등급 | 기준 |
|------|------|
| **A급: Main Portfolio Projects** | 포트폴리오로 보여줄 실제 프로젝트. GitHub pinned 후보 |
| **B급: Practice Labs** | 학습 실습, 수업 과제, 기술 검증용 코드. 학습 기록으로 정리 |
| **C급: Archive Candidates** | 오래된/중복/정리 안 된 저장소. 삭제하지 않고 archive 또는 private 후보 |
| **D급: Sensitive / Cleanup Required** | 민감정보·불필요 빌드 파일 포함. 우선 점검 대상 |

---

## 분류 결과

### 저장소: `code` (monorepo)

| 폴더명 | 등급 | 추천 저장소명 | 분류 이유 | README 정리 | private/archive | 보안 점검 |
|--------|------|--------------|-----------|------------|-----------------|----------|
| `projects/etch-equipment-hmi` | **A급** | `semiconductor-etch-hmi-system` | TwinCAT PLC + WPF + Flask + Scikit-Learn 4계층 통합. 장비시스템SW개발 핵심 결과물 | ✅ 필요 (완료) | — | ⚠️ app.py secret_key 확인 |
| `projects/semitool-hmi` | **A급** | `etch-equipment-control-simulator` | EtherCAT DLL 연동, 레거시→HMI 발전 과정, 장비 제어 구조 포함 | ✅ 필요 (완료) | — | — |
| `projects/flask-csharp-integration` | **A급** | `smart-logistics-plc-system` | Flask↔C# REST 실시간 센서 연동, 정전/지진 시나리오 State Machine | ✅ 필요 (완료) | — | ⚠️ app.secret_key 하드코딩 발견 |
| `projects/unbelievable` | **A급** | `unbelievable-digital-wellbeing` | FastAPI + Next.js 풀스택, CHANGELOG 관리, MVP 수준 완성도 | ✅ 필요 (완료) | — | — |
| `projects/emotion-music-recommendation` | **A급** | `emotion-based-music-recommender` | GPT + Spotify API 감정 음악 추천, MySQL DB, PPT 발표 자료 포함 | ✅ 필요 (완료) | — | — |
| `projects/winforms-gui-portfolio` | **B급** | `winforms-gui-practice` | README에 "연습 결과물"로 직접 명시. WinForms 기초 이벤트 실습 | ✅ 필요 (완료) | — | — |
| `projects/course-registration-system` | **B급** | `csharp-course-registration-practice` | 수강신청 단일 WinForms 앱. 수업 과제 성격 | ✅ 필요 (완료) | — | — |
| `projects/equipment-management-winforms` | **B급** | `winforms-equipment-management-practice` | MySQL 연동 WinForms 앱. 완성도 있으나 수업 실습 수준 | ✅ 필요 (완료) | — | — |
| `projects/digital-detox` | **B급** | — | 코드 없음. 플로우차트 이미지 기획 자료. study/ 폴더로 이동 | — | — | — |

### 별도 저장소

| 저장소명 | 등급 | 분류 이유 | 추천 처리 |
|----------|------|-----------|----------|
| `etch-equipment-system-sw` | **A급** | `semiconductor-etch-hmi-system`과 동일 프로젝트 독립 저장소. 별도 유지 가능 | pinned 후보 |
| `code-` | **C급** | 이름이 `code-`로 끝남. 구버전/중복 저장소로 보임 | private 또는 archive 권장 |

---

## GitHub Pinned Repository 추천 순서

1. `semiconductor-etch-hmi-system` (또는 `etch-equipment-hmi` 폴더 링크)
2. `etch-equipment-control-simulator` (또는 `semitool-hmi` 폴더 링크)
3. `smart-logistics-plc-system` (또는 `flask-csharp-integration` 폴더 링크)
4. `unbelievable-digital-wellbeing` (또는 `unbelievable` 폴더 링크)
5. `emotion-based-music-recommender` (또는 `emotion-music-recommendation` 폴더 링크)
6. (선택) `network-programming-lab` - 통신 기술 학습 기록 보조

---

## GitHub Topics 추천

### A급 프로젝트

**semiconductor-etch-hmi-system (etch-equipment-hmi)**
```
csharp wpf hmi semiconductor etch-equipment equipment-control state-machine recipe alarm plc ethercat
```

**etch-equipment-control-simulator (semitool-hmi)**
```
csharp wpf ethercat hmi equipment-control semiconductor etch-equipment dll-integration
```

**smart-logistics-plc-system (flask-csharp-integration)**
```
flask csharp winforms rest-api sensor-monitoring real-time state-machine iot-prototype
```

**unbelievable-digital-wellbeing (unbelievable)**
```
python fastapi nextjs data-analysis youtube digital-wellbeing dashboard recommendation-system
```

**emotion-based-music-recommender (emotion-music-recommendation)**
```
flask openai spotify mysql emotion-analysis music-recommendation gpt feedback-database
```

### B급 실습
```
csharp winforms practice database mysql learning-project
```

---

## 직접 해야 할 작업 (GitHub 웹에서)

> [github-cleanup-final-checklist.md](./github-cleanup-final-checklist.md) 참조
