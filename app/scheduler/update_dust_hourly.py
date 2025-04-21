# app/scheduler/update_dust_hourly.py

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from app.api.dust_service import fetch_realtime_dust

load_dotenv()

def update_national_dust():
    print("🌫️ 전국 미세먼지 정보 불러오는 중...")
    try:
        data = fetch_realtime_dust("전국")
        Path("db").mkdir(exist_ok=True)
        with open("db/realtime_dust.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("✅ 전국 미세먼지 정보 저장 완료!")
    except Exception as e:
        print(f"❌ API 호출 실패: {e}")

if __name__ == "__main__":
    update_national_dust()
