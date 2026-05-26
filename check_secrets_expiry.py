#!/usr/bin/env python3
"""WOCS 자동화 자산 만료 점검 스크립트.

GitHub Actions에서 매일 실행되어 LinkedIn 액세스 토큰(60일 만료)의
잔여일을 계산하고 GITHUB_OUTPUT 으로 alert_level / days_remaining /
expiry_date 를 내보낸다.

분기:
- 잔여 7일 이하  → alert_level=critical
- 잔여 14일 이하 → alert_level=warning
- 그 외          → alert_level=ok  (워크플로에서 이슈 생성 스킵)

스크립트는 항상 exit 0 으로 종료한다 (워크플로 자체 실패를 만들지 않음).
"""
from __future__ import annotations

import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Final

LIFESPAN_DAYS: Final[int] = 60
CRITICAL_THRESHOLD: Final[int] = 7
WARNING_THRESHOLD: Final[int] = 14
ASSET_NAME: Final[str] = "LI_ACCESS_TOKEN"


def parse_issued_at(value: str) -> date | None:
    """YYYY-MM-DD 문자열을 date 로 변환. 실패 시 None."""
    value = value.strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def classify(days_remaining: int) -> str:
    if days_remaining <= CRITICAL_THRESHOLD:
        return "critical"
    if days_remaining <= WARNING_THRESHOLD:
        return "warning"
    return "ok"


def emit_outputs(**kwargs: str) -> None:
    """GITHUB_OUTPUT 파일에 key=value 라인을 append."""
    out_path = os.environ.get("GITHUB_OUTPUT")
    if not out_path:
        # 로컬 실행 — 콘솔에만 표시
        for key, val in kwargs.items():
            print(f"[local-output] {key}={val}")
        return
    with open(out_path, "a", encoding="utf-8") as fp:
        for key, val in kwargs.items():
            fp.write(f"{key}={val}\n")


def main() -> int:
    issued_at_raw = os.environ.get("LI_TOKEN_ISSUED_AT", "")
    issued_at = parse_issued_at(issued_at_raw)

    if issued_at is None:
        print(f"[warn] LI_TOKEN_ISSUED_AT 미설정 또는 형식 오류: '{issued_at_raw}'")
        print("       gh variable set LI_TOKEN_ISSUED_AT --body YYYY-MM-DD 로 설정 필요")
        print("::warning::LI_TOKEN_ISSUED_AT GitHub Variable 가 비어있어 만료 점검을 건너뜁니다.")
        emit_outputs(alert_level="ok", days_remaining="-1", expiry_date="unknown")
        return 0

    today = date.today()
    expiry = issued_at.fromordinal(issued_at.toordinal() + LIFESPAN_DAYS)
    elapsed = (today - issued_at).days
    days_remaining = LIFESPAN_DAYS - elapsed
    alert = classify(days_remaining)

    print(f"자산: {ASSET_NAME}")
    print(f"발급일: {issued_at.isoformat()}")
    print(f"오늘:   {today.isoformat()}")
    print(f"만료예정: {expiry.isoformat()}")
    print(f"경과: {elapsed}일 / 잔여: {days_remaining}일")
    print(f"alert_level={alert}")

    if alert in ("critical", "warning"):
        # Actions UI 노란 배너 (ASCII-safe: em-dash 대신 하이픈)
        msg = (
            f"::warning::{ASSET_NAME} 만료 임박 - 잔여 {days_remaining}일 "
            f"(만료예정 {expiry.isoformat()}). LinkedIn OAuth 토큰 재발급 필요."
        )
        # Windows cp949 콘솔에서도 안전하도록 fallback
        try:
            print(msg)
        except UnicodeEncodeError:
            print(msg.encode("ascii", "replace").decode("ascii"))

    emit_outputs(
        alert_level=alert,
        days_remaining=str(days_remaining),
        expiry_date=expiry.isoformat(),
        issued_at=issued_at.isoformat(),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
