@echo off
SET GIT="C:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\Git\cmd\git.exe"
SET SRC=C:\Users\son\Documents\한이음\projects\unbelievable
SET DEST=C:\Users\son\Documents\한이음\github-sync\code\projects\unbelievable

echo === [1] 최신 파일 복사 ===
robocopy "%SRC%\backend\app" "%DEST%\backend\app" /E /XD __pycache__ .pytest_cache
robocopy "%SRC%\backend" "%DEST%\backend" requirements.txt test_pipeline.py test_dashboard_explanations.py /IS
robocopy "%SRC%\frontend\src" "%DEST%\frontend\src" /E
robocopy "%SRC%\frontend" "%DEST%\frontend" package.json package-lock.json next.config.js tailwind.config.js tsconfig.json postcss.config.js next-env.d.ts /IS
robocopy "%SRC%\docs" "%DEST%\docs" /E /IS
robocopy "%SRC%\db" "%DEST%\db" /E /IS
copy /Y "%SRC%\.gitignore" "%DEST%\.gitignore"
copy /Y "%SRC%\CHANGELOG.md" "%DEST%\CHANGELOG.md"
copy /Y "%SRC%\README.md" "%DEST%\README.md"
copy /Y "%SRC%\CHANGE_MEMOS.md" "%DEST%\CHANGE_MEMOS.md"
copy /Y "%SRC%\start_unbelievable.bat" "%DEST%\start_unbelievable.bat"

echo.
echo === [2] git 상태 확인 ===
cd /d "%DEST%\..\..\"
%GIT% status --short

echo.
echo === [3] 페이즈 1 commit ===
%GIT% add projects/unbelievable/backend/app/core/takeout_parser.py
%GIT% add projects/unbelievable/backend/app/core/nlp.py
%GIT% add projects/unbelievable/backend/app/core/nlp_enhanced.py
%GIT% add projects/unbelievable/backend/app/core/scoring.py
%GIT% add projects/unbelievable/backend/app/core/survey_scoring.py
%GIT% add projects/unbelievable/backend/app/routes/analysis.py
%GIT% add projects/unbelievable/backend/app/routes/upload.py
%GIT% commit -m "fix(phase1): Takeout parser, duration wording, NLP fallback warning, DSAO label fix"

echo.
echo === [4] 페이즈 2 commit ===
%GIT% add projects/unbelievable/backend/app/data/
%GIT% add projects/unbelievable/backend/app/core/category_loader.py
%GIT% add projects/unbelievable/backend/app/core/scoring_rule_loader.py
%GIT% add projects/unbelievable/backend/app/core/persona_loader.py
%GIT% add projects/unbelievable/backend/app/core/mission_loader.py
%GIT% add projects/unbelievable/backend/app/core/message_loader.py
%GIT% add projects/unbelievable/backend/app/core/category_dictionary.py
%GIT% add projects/unbelievable/backend/app/core/score_config.py
%GIT% add projects/unbelievable/docs/refactoring-hardcoding.md
%GIT% commit -m "refactor(phase2): Extract CATEGORY_DICT/STOP_WORDS/scoring/persona/missions to JSON"

echo.
echo === [5] 페이즈 3 commit ===
%GIT% add projects/unbelievable/backend/app/routes/dashboard.py
%GIT% add projects/unbelievable/backend/app/routes/detox.py
%GIT% add projects/unbelievable/backend/test_dashboard_explanations.py
%GIT% add projects/unbelievable/backend/test_pipeline.py
%GIT% add projects/unbelievable/frontend/src/app/dashboard/page.tsx
%GIT% add projects/unbelievable/docs/dashboard-explanation-and-detox.md
%GIT% commit -m "feat(phase3): explanations field, enriched DSAO, dynamic detox matching, Explanations Card UI"

echo.
echo === [6] 나머지 전체 commit ===
%GIT% add projects/unbelievable/
%GIT% commit -m "chore: gitignore, CHANGELOG, README, schema, frontend assets"

echo.
echo === [7] push ===
%GIT% push origin main

echo.
echo === 완료! commit 목록 ===
%GIT% log --oneline -6
