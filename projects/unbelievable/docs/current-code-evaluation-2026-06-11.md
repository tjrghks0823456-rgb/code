# 2026-06-11 Current Code Evaluation

## Scope

This review evaluates the current `projects/unbelievable` MVP against the existing implementation plan, with emphasis on build health, backend pipeline reliability, dashboard usefulness, and remaining gaps before a public/demo submission.

## Verification Result

- Frontend production build: passed with `npm.cmd run build`.
- Backend syntax check: passed with `python -m py_compile` on key FastAPI/service/scoring files.
- Pipeline test: passed with `test_pipeline.py` after starting the FastAPI server.
- Dashboard explanation scenarios: all 7 scenarios printed success, but the shell command timed out after the final success output instead of exiting cleanly.

## Overall Assessment

The project is no longer just a screen prototype. It has a connected MVP flow:

- Google Takeout upload and parsing.
- Analysis run creation.
- Dashboard summary API.
- 6-axis score details.
- DSAO type mapping.
- Detox mission generation.
- Frontend dashboard, upload, survey, mission, and type pages.

For a school/capstone demonstration, the code is in a good MVP state. For production or external users, the main risks are data reliability, persistence/auth, and the fact that several "smart" results still depend on fallback or heuristic logic.

## Strengths

1. The plan's three major improvement areas are mostly implemented.
   - Takeout parsing, duration warnings, score details, dashboard warnings, and compact dashboard UI are all present.
   - The frontend build succeeds, so the UI work is not just static markup.

2. The backend API contract is reasonably complete.
   - Upload, analysis, dashboard, detox, survey, and tracker routers are registered.
   - Tests verify the upload -> analysis -> dashboard flow.

3. The scoring system is explainable.
   - Score details expose confidence, warnings, component values, and data quality flags.
   - This is stronger than a black-box "AI score" and is useful for presentations.

4. Fallback behavior is deliberate.
   - Missing API keys and unavailable NLP tools do not crash the app.
   - The UI and backend label duration/NLP limitations instead of pretending everything is exact.

## Main Issues To Fix Next

1. User/session persistence is still MVP-only.
   - The app uses a fixed default user id and browser `localStorage` for survey/run state.
   - This is acceptable for a demo, but not for multiple real users.
   - Relevant files: `backend/app/core/config.py`, `frontend/src/utils/apiConfig.ts`, `frontend/src/utils/surveyStorage.ts`.

2. Supabase is not the guaranteed source of truth.
   - The database layer can fall back to local in-memory MockDB when Supabase is disabled or fails.
   - This protects demos, but results can disappear after process restart.
   - Relevant file: `backend/app/core/database.py`.

3. Confidence can look internally inconsistent.
   - In the pipeline test, some component fields showed meaningful confidence internally, while final axis confidence became `0.0` because fallback/mock post-processing penalized sensitive axes.
   - This is conservative, but users may read it as "score is invalid" even when the score is still heuristically useful.
   - Relevant file: `backend/app/core/scoring.py`.

4. Duration logic is still not actual watch time.
   - The implementation correctly warns about missing/estimated duration, but the product must keep wording careful.
   - Do not market this as exact viewing time.
   - Relevant files: `backend/app/services/upload_service.py`, `frontend/src/app/dashboard/page.tsx`.

5. Test scripts need a cleaner lifecycle.
   - `test_pipeline.py` assumes the API server is already running.
   - `test_dashboard_explanations.py` printed all scenario successes, but the shell command timed out instead of finishing cleanly.
   - Add a pytest/TestClient version or make scripts start/stop their own server.

6. CORS is wide open.
   - `allow_origins=["*"]` is fine for a prototype, but should become environment-specific before deployment.
   - Relevant file: `backend/app/main.py`.

## Difference From Original Plan

The current code is broader than the implementation plan in several places:

- Added beyond the plan:
  - Survey flow.
  - DSAO type collection.
  - Mission generation and mission completion UI.
  - Tracker-related routes.
  - Local MockDB fallback.

- Matches the plan:
  - Takeout parsing improvements.
  - Duration limitation/warning handling.
  - TDS/category confidence handling.
  - Dashboard warning banners.
  - Score component accordions.
  - Interest graph tab/compact presentation.
  - Next.js build verification.

- Still below the plan or roadmap:
  - Supabase Auth/user session integration.
  - Persisted survey scores in Supabase.
  - YouTube Data API as a real duration metadata source in normal runs.
  - Embedding/deep-learning interest classification.
  - Long-term, high-volume Takeout analysis.

## Priority Recommendation

1. Replace fixed MVP user/session handling with real user identity and persistent run ownership.
2. Convert current script tests into repeatable pytest/TestClient tests that do not require a manually running server.
3. Make confidence labels clearer: separate "score confidence", "data quality", and "fallback source" so users understand why a value is useful but low-confidence.
4. Lock CORS and environment configuration for deployment.
5. Keep the dashboard compact, but reduce explanatory density in the technical panel for normal users and keep full details behind an advanced toggle.

## Bottom Line

The current code is a solid MVP and presentation-ready if framed honestly as a heuristic media-consumption diagnostic tool. It is not yet production-ready because identity, persistence, exact watch-time measurement, and model-grade classification are still prototype/fallback areas.
