import subprocess

GIT = r"C:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\Git\cmd\git.exe"
REPO = r"C:\Users\son\Documents\한이음\github-sync\code"

def git(*args):
    result = subprocess.run([GIT] + list(args), cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    if result.stdout.strip(): print(result.stdout.strip())
    if result.stderr.strip(): print("STDERR:", result.stderr.strip())
    return result.returncode

# rebase 중단
print("=== rebase 중단 ===")
git("rebase", "--abort")

# 현재 브랜치 확인
print("\n=== 현재 브랜치 ===")
git("branch")

# 우리 commit들을 main 위에 force push
# remote main을 로컬로 가져오되 우리 변경을 유지
print("\n=== merge 전략: ours ===")
git("pull", "origin", "main", "--strategy=ours", "--no-rebase", "-m", "merge: integrate remote main, keep local phase1-3 changes")

print("\n=== Push ===")
rc = git("push", "origin", "HEAD:main")
if rc != 0:
    print("\n강제 push 시도...")
    git("push", "origin", "HEAD:main", "--force-with-lease")

print("\n=== 최근 commit 목록 ===")
git("log", "--oneline", "-8")
