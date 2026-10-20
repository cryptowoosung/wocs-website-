#!/usr/bin/env bash
# Vercel "Ignored Build Step" (vercel.json ignoreCommand) — 2026-10-20
#   exit 0 → 빌드 건너뜀 / exit 1 → 빌드 진행
# 마지막 배포 이후 바뀐 파일이 모두 .vercelignore 대상(파이썬 스크립트·워크플로·문서 등)이면
# 사이트 결과물이 같으므로 배포하지 않는다. 판단이 불확실하면 항상 빌드한다.

BASE="${VERCEL_GIT_PREVIOUS_SHA:-}"
if [ -z "$BASE" ] || ! git cat-file -e "${BASE}^{commit}" 2>/dev/null; then
  echo "이전 배포 커밋을 찾을 수 없음 → 빌드"
  exit 1
fi

CHANGED=$(git -c core.quotepath=off diff --name-only "$BASE" HEAD)
if [ -z "$CHANGED" ]; then
  echo "변경 파일 없음 → 건너뜀"
  exit 0
fi

IGNORED=$(git -c core.quotepath=off ls-files -c -i --exclude-from=.vercelignore)
RELEVANT=$(printf '%s\n' "$CHANGED" | grep -vxF -f <(printf '%s\n' "$IGNORED") || true)

if [ -z "$RELEVANT" ]; then
  echo "사이트 배포 대상 변경 없음 → 건너뜀"
  exit 0
fi

echo "사이트 배포 대상 변경 있음 → 빌드:"
printf '%s\n' "$RELEVANT" | head -20
exit 1
