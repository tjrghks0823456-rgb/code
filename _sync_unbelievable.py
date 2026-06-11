import subprocess
import shutil
import os

GIT = r"C:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\Git\cmd\git.exe"
SRC = r"C:\Users\son\Documents\한이음\projects\unbelievable"
REPO = r"C:\Users\son\Documents\한이음\github-sync\code"
DEST = os.path.join(REPO, "projects", "unbelievable")

def git(*args, cwd=REPO):
    result = subprocess.run([GIT] + list(args), cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    print(result.stdout.strip())
    if result.stderr.strip():
        print("STDERR:", result.stderr.strip())
    return result.returncode

def copy_tree(src, dst, ignore_dirs=None):
    ignore_dirs = ignore_dirs or []
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        if item in ignore_dirs:
            continue
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copy_tree(s, d, ignore_dirs)
        else:
            shutil.copy2(s, d)

print("=== [1] 파일 복사 중 ===")

# backend/app
copy_tree(
    os.path.join(SRC, "backend", "app"),
    os.path.join(DEST, "backend", "app"),
    ignore_dirs=["__pycache__", ".pytest_cache"]
)

# backend root files
for f in ["requirements.txt", "test_pipeline.py", "test_dashboard_explanations.py"]:
    src_f = os.path.join(SRC, "backend", f)
    if os.path.exists(src_f):
        shutil.copy2(src_f, os.path.join(DEST, "backend", f))

# frontend/src
copy_tree(
    os.path.join(SRC, "frontend", "src"),
    os.path.join(DEST, "frontend", "src")
)

# frontend root files
for f in ["package.json", "package-lock.json", "next.config.js",
          "tailwind.config.js", "tsconfig.json", "postcss.config.js",
          "next-env.d.ts", "dev-server.js", ".env.local.example"]:
    src_f = os.path.join(SRC, "frontend", f)
    if os.path.exists(src_f):
        shutil.copy2(src_f, os.path.join(DEST, "frontend", f))

# docs, db
copy_tree(os.path.join(SRC, "docs"), os.path.join(DEST, "docs"))
copy_tree(os.path.join(SRC, "db"), os.path.join(DEST, "db"))

# root files
for f in [".gitignore", "CHANGELOG.md", "README.md", "CHANGE_MEMOS.md", "start_unbelievable.bat"]:
    src_f = os.path.join(SRC, f)
    if os.path.exists(src_f):
        shutil.copy2(src_f, os.path.join(DEST, f))

print("복사 완료!")

print("\n=== [2] git config ===")
git("config", "user.email", "tjrghks0823456@gmail.com")
git("config", "user.name", "tjrghks0823456-rgb")

print("\n=== [3] Phase 1 commit ===")
phase1_files = [
    "projects/unbelievable/backend/app/core/takeout_parser.py",
    "projects/unbelievable/backend/app/core/nlp.py",
    "projects/unbelievable/backend/app/core/nlp_enhanced.py",
    "projects/unbelievable/backend/app/core/scoring.py",
    "projects/unbelievable/backend/app/core/survey_scoring.py",
    "projects/unbelievable/backend/app/routes/analysis.py",
    "projects/unbelievable/backend/app/routes/upload.py",
]
for f in phase1_files:
    if os.path.exists(os.path.join(REPO, f)):
        git("add", f)
git("commit", "-m", "fix(phase1): Takeout parser, duration wording, NLP fallback warning, DSAO label fix")

print("\n=== [4] Phase 2 commit ===")
phase2_files = [
    "projects/unbelievable/backend/app/data",
    "projects/unbelievable/backend/app/core/category_loader.py",
    "projects/unbelievable/backend/app/core/scoring_rule_loader.py",
    "projects/unbelievable/backend/app/core/persona_loader.py",
    "projects/unbelievable/backend/app/core/mission_loader.py",
    "projects/unbelievable/backend/app/core/message_loader.py",
    "projects/unbelievable/backend/app/core/category_dictionary.py",
    "projects/unbelievable/backend/app/core/score_config.py",
    "projects/unbelievable/docs/refactoring-hardcoding.md",
]
for f in phase2_files:
    git("add", f)
git("commit", "-m", "refactor(phase2): Extract CATEGORY_DICT/STOP_WORDS/scoring/persona/missions to JSON")

print("\n=== [5] Phase 3 commit ===")
phase3_files = [
    "projects/unbelievable/backend/app/routes/dashboard.py",
    "projects/unbelievable/backend/app/routes/detox.py",
    "projects/unbelievable/backend/test_dashboard_explanations.py",
    "projects/unbelievable/backend/test_pipeline.py",
    "projects/unbelievable/frontend/src/app/dashboard/page.tsx",
    "projects/unbelievable/docs/dashboard-explanation-and-detox.md",
]
for f in phase3_files:
    if os.path.exists(os.path.join(REPO, f)):
        git("add", f)
git("commit", "-m", "feat(phase3): explanations field, enriched DSAO, dynamic detox matching, Explanations Card UI")

print("\n=== [6] Chore commit (나머지 전체) ===")
git("add", "projects/unbelievable/")
git("commit", "-m", "chore: gitignore, CHANGELOG, README, schema, frontend assets")

print("\n=== [7] Push ===")
git("push", "origin", "main")

print("\n=== 완료! 최근 commit 목록 ===")
git("log", "--oneline", "-6")
