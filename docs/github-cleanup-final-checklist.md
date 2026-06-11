# GitHub 정리 후 직접 해야 할 작업 체크리스트

> 이 파일에 있는 작업들은 GitHub 웹 또는 로컬에서 직접 처리해야 합니다.  
> 아래 항목들은 API로 자동화하기 어렵거나 직접 판단이 필요한 작업입니다.

---

## 1. 저장소 이름 변경 (GitHub Settings에서)

> 설정 → Repository name → Rename

현재 `code` 저장소는 monorepo 방식으로 유지합니다.  
별도 저장소인 `etch-equipment-system-sw`는 아래처럼 이름을 바꿀 수 있습니다.

| 현재 이름 | 추천 이름 | 우선순위 |
|-----------|-----------|----------|
| `etch-equipment-system-sw` | `semiconductor-etch-hmi-system` | 🔴 높음 |
| `code-` | — | 🟡 private 또는 archive 처리 권장 |

---

## 2. Pinned Repository 설정

> GitHub 프로필 페이지 → Customize your pins

아래 순서로 pinned 설정을 권장합니다.

1. ☐ `semiconductor-etch-hmi-system` (또는 `etch-equipment-system-sw`)
2. ☐ `code` (monorepo) - 세부 프로젝트 폴더 링크를 README에 명시
3. 필요시 개별 저장소 추가

---

## 3. GitHub Topics 추가

> 저장소 → About → ⚙️ → Topics

**`etch-equipment-system-sw` (또는 개명 후):**
```
csharp wpf hmi semiconductor etch-equipment equipment-control state-machine recipe alarm plc ethercat
```

**`code` (monorepo):**
```
csharp wpf python flask portfolio semiconductor equipment-control
```

---

## 4. Archive 또는 Private 처리

> 저장소 → Settings → Danger Zone → Archive this repository

| 저장소 | 권장 처리 | 이유 |
|--------|-----------|------|
| `code-` | private 또는 archive | 이름이 `code-`로 끝나는 구버전 저장소로 보임. 내용 확인 후 처리 |

---

## 5. 보안 수정 (코드 직접 수정 필요)

> 아래 항목은 코드 변경이 필요하므로 직접 처리해야 합니다.

☐ `projects/flask-csharp-integration/Flask_Backend/app.py`
- 현재: `app.secret_key = "하드코딩된 값"`
- 변경: `app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-key")`
- `.env.example` 파일 추가:
  ```
  FLASK_SECRET_KEY=your-secret-key-here
  ```
- `.gitignore`에 `.env` 추가

---

## 6. README 최종 확인

☐ `code` 저장소 루트 README.md - 전체 구조 안내 확인  
☐ `projects/README.md` - 5개 Main Portfolio 프로젝트 소개 확인  
☐ `study/README.md` - 4개 Practice Labs 소개 확인  
☐ 각 프로젝트 폴더 README.md - 상세 내용 확인  

---

## 7. GitHub Profile README 적용

> GitHub에서 자신의 username과 동일한 이름의 저장소 생성 (예: `tjrghks0823456-rgb/tjrghks0823456-rgb`)
> 그 저장소의 `README.md`에 `PROFILE_README_DRAFT.md` 내용을 붙여넣기

☐ `tjrghks0823456-rgb` 저장소 생성  
☐ `PROFILE_README_DRAFT.md` 내용을 저장소 `README.md`에 붙여넣기  
☐ 저장소를 public으로 설정  

---

## 완료 기준

- [ ] 면접관이 GitHub 프로필을 봤을 때 10초 안에 "장비 제어 SW 개발자 지망"임을 알 수 있는가?
- [ ] Main Portfolio 5개 프로젝트에 각각 상세 README가 있는가?
- [ ] Practice Labs가 프로젝트와 명확히 분리되어 있는가?
- [ ] 민감정보가 노출된 파일이 없는가?
- [ ] pinned repository가 올바르게 설정되어 있는가?
