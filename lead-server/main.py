"""
WOCS Lead Capture Backend Server
- 리드 데이터 수신
- 구글시트 저장
- 텔레그램 알림 발송

실행: uvicorn main:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
from datetime import datetime

app = FastAPI(title="WOCS Lead Capture API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ══════════════════════════════════════
# ★ 설정 — 아래 값을 실제 값으로 교체하세요
# ══════════════════════════════════════
TELEGRAM_BOT_TOKEN = "여기에_텔레그램_봇_토큰"
TELEGRAM_CHAT_ID = "여기에_텔레그램_채팅_ID"
GOOGLE_SHEET_NAME = "WOCS_리드_DB"
CREDENTIALS_FILE = "credentials.json"  # Google 서비스 계정 키 파일


@app.get("/")
async def root():
    return {"status": "WOCS Lead Capture API is running"}


@app.post("/lead")
async def receive_lead(request: Request):
    data = await request.json()

    name = data.get("name", "")
    phone = data.get("phone", "")
    location = data.get("location", "")
    product = data.get("product", "")
    page = data.get("page", "")
    lang = data.get("lang", "ko")
    source = data.get("source", "popup")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1) 구글시트 저장
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open(GOOGLE_SHEET_NAME).sheet1
        sheet.append_row([timestamp, name, phone, location, product, page, lang, source])
        print(f"✅ 시트 저장 완료: {name} / {phone}")
    except Exception as e:
        print(f"⚠️ 시트 저장 실패: {e}")

    # 2) 텔레그램 알림
    try:
        if TELEGRAM_BOT_TOKEN != "여기에_텔레그램_봇_토큰":
            product_names = {
                "all": "전체", "s-series": "S-시리즈",
                "d-series": "D-시리즈 돔", "signature": "Signature 시리즈",
                "modular": "모듈러 시스템"
            }
            product_display = product_names.get(product, product)

            msg = (
                f"🚨 [신규 리드 유입]\n"
                f"━━━━━━━━━━━━━━\n"
                f"👤 이름: {name}\n"
                f"📱 연락처: {phone}\n"
                f"📍 지역: {location or '미입력'}\n"
                f"🏕 관심제품: {product_display}\n"
                f"🌐 유입페이지: {page}\n"
                f"🕐 시간: {timestamp}\n"
                f"━━━━━━━━━━━━━━"
            )

            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": msg,
                    "parse_mode": "HTML"
                })
            print(f"✅ 텔레그램 알림 발송: {resp.status_code}")
    except Exception as e:
        print(f"⚠️ 텔레그램 실패: {e}")

    return {"status": "ok", "timestamp": timestamp}


# 견적 폼 전용 엔드포인트 (더 많은 필드)
@app.post("/quote")
async def receive_quote(request: Request):
    data = await request.json()

    name = data.get("name", "")
    phone = data.get("phone", "")
    email = data.get("email", "")
    country = data.get("country", "")
    company = data.get("company", "")
    region = data.get("region", "")
    area = data.get("area", "")
    budget = data.get("budget", "")
    target_date = data.get("targetDate", "")
    models = data.get("models", [])
    message = data.get("message", "")
    page = data.get("page", "")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 구글시트 저장
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open(GOOGLE_SHEET_NAME).worksheet("견적요청")
        models_str = ", ".join(models) if isinstance(models, list) else str(models)
        sheet.append_row([
            timestamp, name, phone, email, country, company,
            region, area, budget, target_date, models_str, message, page
        ])
    except Exception as e:
        print(f"⚠️ 견적 시트 저장 실패: {e}")

    # 텔레그램 알림
    try:
        if TELEGRAM_BOT_TOKEN != "여기에_텔레그램_봇_토큰":
            models_str = ", ".join(models) if isinstance(models, list) else str(models)
            msg = (
                f"📋 [신규 견적 요청]\n"
                f"━━━━━━━━━━━━━━\n"
                f"👤 이름: {name}\n"
                f"📱 연락처: {phone}\n"
                f"📧 이메일: {email}\n"
                f"🌍 국가: {country}\n"
                f"🏢 회사: {company or '미입력'}\n"
                f"📍 시공지역: {region}\n"
                f"📐 면적: {area}\n"
                f"💰 예산: {budget}\n"
                f"📅 오픈목표: {target_date or '미입력'}\n"
                f"🏕 모델: {models_str}\n"
                f"💬 메시지: {message[:100] if message else '없음'}\n"
                f"🕐 시간: {timestamp}\n"
                f"━━━━━━━━━━━━━━"
            )
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            async with httpx.AsyncClient() as client:
                await client.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    except Exception as e:
        print(f"⚠️ 텔레그램 실패: {e}")

    return {"status": "ok", "timestamp": timestamp}
