#!/usr/bin/env bash
# 블로그 발행 큐 (blog-queue 브랜치) 공용 스크립트 — 2026-10-20 하루 1회 배포 구조
#   prepare : blog-queue 브랜치로 전환하고 main 의 최신 변경을 합친다 (없으면 main 에서 새로 만든다)
#   push    : 생성된 글을 blog-queue 에 커밋·푸시한다 (main 에는 푸시하지 않음)
# main 반영은 daily-publish.yml 이 매일 09:00 KST 에 한 번만 한다.
# 사용: bash scripts/blog_queue.sh prepare
#       bash scripts/blog_queue.sh push "커밋 메시지" [git add 경로...]
set -euo pipefail

QUEUE_BRANCH="blog-queue"

case "${1:-}" in
  prepare)
    git fetch origin main
    if git ls-remote --exit-code --heads origin "$QUEUE_BRANCH" >/dev/null; then
      git fetch origin "$QUEUE_BRANCH"
      git checkout -B "$QUEUE_BRANCH" "origin/$QUEUE_BRANCH"
      # 수동 수정(main)을 큐에 반영 — 충돌 시 실패시켜 Telegram 알림으로 넘긴다
      if ! git merge --no-edit "origin/main"; then
        git merge --abort || true
        echo "blog-queue ↔ main 병합 충돌: main 의 blog-data.js/content 수동 수정과 큐의 글이 겹침." >&2
        echo "해결: 로컬에서 blog-queue 에 main 을 병합해 충돌 해결 후 push, 또는 daily-publish 수동 실행 후 재시도" >&2
        exit 1
      fi
    else
      git checkout -B "$QUEUE_BRANCH" "origin/main"
    fi
    echo "큐 브랜치 준비 완료: $(git rev-parse --short HEAD)"
    ;;
  push)
    MSG="${2:?커밋 메시지가 필요합니다}"
    shift 2
    if [ "$#" -gt 0 ]; then git add "$@"; else git add -A; fi
    git diff --staged --quiet || git commit -m "$MSG"
    # daily-publish 가 그사이 큐를 초기화했으면 non-fast-forward 거부 → 새 큐 위로 rebase 후 1회 재시도
    if ! git push origin "HEAD:refs/heads/$QUEUE_BRANCH"; then
      git pull --rebase origin "$QUEUE_BRANCH"
      git push origin "HEAD:refs/heads/$QUEUE_BRANCH"
    fi
    echo "큐에 적재 완료 (main 반영은 매일 09:00 KST daily-publish)"
    ;;
  *)
    echo "사용법: $0 prepare | push \"메시지\" [경로...]" >&2
    exit 2
    ;;
esac
