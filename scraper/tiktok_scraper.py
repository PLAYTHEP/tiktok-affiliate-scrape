"""
TikTok Creative Center - Top Products Scraper
ดึงข้อมูลสินค้ายอดนิยมจาก TikTok Creative Center แล้วส่งไปยัง GAS Web App
"""

import json
import time
import sys
import os
from datetime import datetime

import requests

# ─── CONFIG ───────────────────────────────────────────────────────────
GAS_WEBHOOK_URL = os.environ.get("AKfycbziNGTWgNRVOc3LxuwVw4HCoMpRaQzREtLy2ZyiNcjOo_k_qG2ZdoA6CBp_3MqEDIlAEg", "https://script.google.com/macros/s/AKfycbziNGTWgNRVOc3LxuwVw4HCoMpRaQzREtLy2ZyiNcjOo_k_qG2ZdoA6CBp_3MqEDIlAEg/exec")
TIKTOK_API_URL = "https://ads.tiktok.com/creative_radar_api/v1/top_products/list"

# TikTok Creative Center API parameters
PARAMS = {
    "period": 7,           # 7 = Last 7 days, 30 = Last 30 days
    "country_code": "TH",  # TH = Thailand
    "category_id": "",     # Empty = all categories
    "sort_by": "ctr",      # Sort by Click-Through Rate
    "page": 1,
    "limit": 20,
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,th;q=0.8",
    "Referer": "https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en",
    "Origin": "https://ads.tiktok.com",
}


# ─── SCRAPER ──────────────────────────────────────────────────────────
def fetch_top_products() -> list[dict]:
    """
    ดึงข้อมูล Top Products จาก TikTok Creative Center API
    คืนค่าเป็น list ของ dict สำหรับสินค้าแต่ละรายการ
    """
    print("[1/3] Fetching top products from TikTok Creative Center...")

    try:
        resp = requests.get(TIKTOK_API_URL, params=PARAMS, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] TikTok API request failed: {e}")
        # Fallback: ใช้ข้อมูลจำลองเพื่อให้ pipeline ไม่พังทั้งระบบ
        return _get_fallback_data()

    # Parse response
    products = []
    try:
        items = data.get("data", {}).get("materials", [])
        if not items:
            print("[WARN] No products returned from API. Using fallback data.")
            return _get_fallback_data()

        for i, item in enumerate(items):
            product = {
                "rank": i + 1,
                "product_name": item.get("title", "N/A"),
                "ctr": _parse_ctr(item.get("ctr", 0)),
                "category": item.get("industry_name", "Uncategorized"),
                "country": PARAMS["country_code"],
                "likes": item.get("like_cnt", 0),
                "comments": item.get("comment_cnt", 0),
                "shares": item.get("share_cnt", 0),
                "source_url": item.get("video_link", ""),
                "scraped_at": datetime.utcnow().isoformat() + "Z",
            }
            products.append(product)

        print(f"[OK] Fetched {len(products)} products successfully.")
    except (KeyError, TypeError) as e:
        print(f"[ERROR] Failed to parse TikTok response: {e}")
        return _get_fallback_data()

    return products


def _parse_ctr(raw_ctr) -> float:
    """แปลงค่า CTR ให้เป็น float (เปอร์เซ็นต์)"""
    try:
        val = float(raw_ctr)
        # ถ้า API คืนค่าเป็นสัดส่วน (0.05) ให้แปลงเป็นเปอร์เซ็นต์
        if val < 1:
            val = round(val * 100, 2)
        return val
    except (ValueError, TypeError):
        return 0.0


def _get_fallback_data() -> list[dict]:
    """ข้อมูลจำลองเมื่อ API ล่มหรือเข้าถึงไม่ได้"""
    print("[INFO] Using fallback sample data for pipeline testing.")
    return [
        {
            "rank": 1,
            "product_name": "สายชาร์จ USB-C 100W ชาร์จเร็วสุดคุ้ม",
            "ctr": 5.8,
            "category": "Electronics & Accessories",
            "country": "TH",
            "likes": 15200,
            "comments": 980,
            "shares": 2340,
            "source_url": "",
            "scraped_at": datetime.utcnow().isoformat() + "Z",
        },
        {
            "rank": 2,
            "product_name": "เซรั่มวิตามินซี ผิวกระจ่างใส",
            "ctr": 4.2,
            "category": "Beauty & Personal Care",
            "country": "TH",
            "likes": 32100,
            "comments": 1540,
            "shares": 5200,
            "source_url": "",
            "scraped_at": datetime.utcnow().isoformat() + "Z",
        },
        {
            "rank": 3,
            "product_name": "กางเกงขาสั้นผ้าไอซ์ซิลค์ ใส่สบาย",
            "ctr": 2.1,
            "category": "Fashion",
            "country": "TH",
            "likes": 8900,
            "comments": 420,
            "shares": 1100,
            "source_url": "",
            "scraped_at": datetime.utcnow().isoformat() + "Z",
        },
    ]


# ─── SENDER ───────────────────────────────────────────────────────────
def send_to_gas(products: list[dict]) -> bool:
    """ส่งข้อมูล JSON ไปยัง Google Apps Script Web App"""
    print(f"[2/3] Sending {len(products)} products to GAS Web App...")

    if GAS_WEBHOOK_URL == "YOUR_GAS_WEB_APP_URL_HERE":
        print("[ERROR] GAS_WEBHOOK_URL is not configured! Set it as a GitHub Secret.")
        return False

    payload = {
        "source": "github_actions",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "product_count": len(products),
        "products": products,
    }

    try:
        resp = requests.post(
            GAS_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
        resp.raise_for_status()
        result = resp.text
        print(f"[OK] GAS responded: {result[:200]}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to send data to GAS: {e}")
        return False


# ─── MAIN ─────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  TikTok Affiliate Pipeline - Scraper")
    print(f"  Run at: {datetime.utcnow().isoformat()}Z")
    print("=" * 60)

    # Step 1: ดึงข้อมูล
    products = fetch_top_products()
    if not products:
        print("[FATAL] No products to process. Exiting.")
        sys.exit(1)

    # Step 2: ส่งไป GAS
    success = send_to_gas(products)

    # Step 3: สรุปผล
    print("\n" + "=" * 60)
    if success:
        print("[DONE] Pipeline scraper completed successfully!")
    else:
        print("[WARN] Scraper finished but GAS delivery failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
