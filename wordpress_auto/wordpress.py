"""
WordPress REST API 클라이언트
- Basic Auth (Application Password) 인증
- 카테고리 생성/조회, 포스트 생성
"""

import logging
import os
from typing import List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)

WP_BASE_URL = os.environ.get("WP_BASE_URL", "https://candlejs6.mycafe24.com")
WP_USERNAME = os.environ.get("WP_USERNAME", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "")


def _api_url(endpoint: str) -> str:
    return f"{WP_BASE_URL.rstrip('/')}/wp-json/wp/v2/{endpoint.lstrip('/')}"


def _auth() -> Tuple[str, str]:
    return (WP_USERNAME, WP_APP_PASSWORD)


def _check_response(resp: requests.Response, action: str) -> dict:
    if resp.status_code not in (200, 201):
        logger.error(
            "%s failed: %s %s",
            action,
            resp.status_code,
            resp.text[:500],
        )
        resp.raise_for_status()
    return resp.json()


# ─── Categories ──────────────────────────────────────────


def get_or_create_category(name: str) -> Optional[int]:
    """카테고리 이름으로 조회, 없으면 생성. 실패 시 None 반환."""
    try:
        # 조회
        resp = requests.get(
            _api_url("categories"),
            params={"search": name, "per_page": 10},
            auth=_auth(),
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            logger.warning("Category search failed (%s), skipping: %s", resp.status_code, name)
            return None
        data = resp.json()
        if not isinstance(data, list):
            logger.warning("Category search returned non-list, skipping: %s", name)
            return None
        for cat in data:
            if cat.get("name") == name:
                logger.info("Category found: %s (id=%d)", name, cat["id"])
                return cat["id"]

        # 생성
        resp = requests.post(
            _api_url("categories"),
            json={"name": name},
            auth=_auth(),
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            logger.warning("Category create failed (%s), skipping: %s", resp.status_code, name)
            return None
        cat = resp.json()
        logger.info("Category created: %s (id=%d)", name, cat["id"])
        return cat["id"]
    except Exception as e:
        logger.warning("Category API error for '%s': %s", name, e)
        return None


# ─── Posts ───────────────────────────────────────────────


def create_post(
    title: str,
    content_html: str,
    categories: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    meta_description: str = "",
    focus_keyword: str = "",
) -> Tuple[int, str]:
    """
    포스트 생성 → (post_id, post_url) 반환

    - categories: 카테고리 이름 리스트 → 자동 생성/조회
    - tags: 태그 이름 리스트 (WP가 자동 생성)
    """
    # 카테고리 ID 확보 (실패 시 None → 필터링)
    cat_ids = []
    if categories:
        for name in categories:
            cid = get_or_create_category(name)
            if cid is not None:
                cat_ids.append(cid)

    # 태그 ID 확보 (실패 시 None → 필터링)
    tag_ids = []
    if tags:
        for tag_name in tags:
            tid = _get_or_create_tag(tag_name)
            if tid is not None:
                tag_ids.append(tid)

    payload = {
        "title": title,
        "content": content_html,
        "status": "publish",
    }
    if cat_ids:
        payload["categories"] = cat_ids
    if tag_ids:
        payload["tags"] = tag_ids

    resp = requests.post(
        _api_url("posts"),
        json=payload,
        auth=_auth(),
        timeout=30,
    )
    post = _check_response(resp, "create post")
    post_id = post["id"]
    post_url = post["link"]
    logger.info("Post created: id=%d url=%s", post_id, post_url)

    # Yoast SEO 메타 (스텁)
    if meta_description or focus_keyword:
        update_yoast_meta(post_id, focus_keyword, meta_description)

    return post_id, post_url


def _get_or_create_tag(name: str) -> Optional[int]:
    """태그 이름으로 조회, 없으면 생성. 실패 시 None 반환."""
    try:
        resp = requests.get(
            _api_url("tags"),
            params={"search": name, "per_page": 10},
            auth=_auth(),
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            logger.warning("Tag search failed (%s), skipping: %s", resp.status_code, name)
            return None
        data = resp.json()
        if not isinstance(data, list):
            return None
        for tag in data:
            if tag.get("name") == name:
                return tag["id"]

        resp = requests.post(
            _api_url("tags"),
            json={"name": name},
            auth=_auth(),
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            logger.warning("Tag create failed (%s), skipping: %s", resp.status_code, name)
            return None
        tag = resp.json()
        logger.info("Tag created: %s (id=%d)", name, tag["id"])
        return tag["id"]
    except Exception as e:
        logger.warning("Tag API error for '%s': %s", name, e)
        return None


# ─── Yoast SEO (스텁) ───────────────────────────────────


def update_yoast_meta(
    post_id: int,
    focus_keyword: str = "",
    meta_description: str = "",
) -> None:
    """
    Yoast SEO 메타 업데이트 (스텁)

    Yoast REST API 필드:
      yoast_head_json._yoast_wpseo_focuskw
      yoast_head_json._yoast_wpseo_metadesc

    Yoast Premium + REST API 활성화 시 아래 코드 활성화:
    """
    # resp = requests.post(
    #     _api_url(f"posts/{post_id}"),
    #     json={
    #         "meta": {
    #             "_yoast_wpseo_focuskw": focus_keyword,
    #             "_yoast_wpseo_metadesc": meta_description,
    #         }
    #     },
    #     auth=_auth(),
    #     timeout=15,
    # )
    # _check_response(resp, "update yoast meta")
    logger.info(
        "Yoast meta stub: post_id=%d keyword='%s'",
        post_id,
        focus_keyword,
    )
