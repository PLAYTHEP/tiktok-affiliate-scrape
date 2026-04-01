# 🚀 Automated TikTok Affiliate Pipeline

ระบบดึงข้อมูลสินค้ามาแรงจาก TikTok Creative Center → สร้างสคริปต์ขายของด้วย AI → แจ้งเตือนเข้ามือถืออัตโนมัติ

## 📐 สถาปัตยกรรมระบบ

```
GitHub Actions (ทุก 12 ชม.)
    │
    ▼
Python Scraper ─── ดึง Top Products จาก TikTok
    │
    ▼ (POST JSON)
Google Apps Script Web App
    ├── บันทึกลง Sheet: Raw_Data
    ├── สุ่มเรียก AI (Gemini / Groq) → สร้างสคริปต์ 3 โทน + Image Prompts
    ├── บันทึกลง Sheet: AI_Content
    └── Smart Filter (CTR > 3%)
         ├── ✅ ส่ง Telegram + LINE
         └── ❌ Silent Log เท่านั้น
```

## 📁 โครงสร้างไฟล์

```
affiliate-pipeline/
├── .github/workflows/main.yml    ← GitHub Actions (รันทุก 12 ชม.)
├── scraper/
│   ├── tiktok_scraper.py         ← Python scraper
│   └── requirements.txt
├── gas_webapp.gs                 ← Google Apps Script (copy ไปวางใน GAS Editor)
└── README.md
```

## 🛠️ วิธีตั้งค่า

### 1. Google Apps Script

1. ไปที่ [script.google.com](https://script.google.com) → สร้างโปรเจกต์ใหม่
2. Copy โค้ดจาก `gas_webapp.gs` ไปวาง
3. ใส่ API Keys ของคุณใน object `CFG`
4. Deploy → Web App → Execute as: **Me** → Access: **Anyone**
5. Copy URL ของ Web App ไว้

### 2. GitHub Repository

1. Push โค้ดขึ้น GitHub
2. ไปที่ Settings → Secrets → Actions
3. เพิ่ม Secret: `GAS_WEBHOOK_URL` = URL จากข้อ 1

### 3. ทดสอบ

- **ทดสอบ GAS**: รันฟังก์ชัน `TEST_fullPipeline()` ใน Apps Script Editor
- **ทดสอบ GitHub Actions**: ไปที่ tab Actions → Run workflow manually

## 📊 Google Sheets ที่ระบบสร้างอัตโนมัติ

| Sheet | รายละเอียด |
|-------|-----------|
| `Raw_Data` | ข้อมูลดิบสินค้าทั้งหมดจาก TikTok |
| `AI_Content` | สคริปต์ที่ AI สร้างให้ (3 โทน + Image Prompts) |
| `Notification_Log` | บันทึกสถานะการแจ้งเตือน + Smart Filter |

## ⚙️ การปรับแต่ง

- **CTR Threshold**: แก้ `CFG.CTR_THRESHOLD` (ค่าเริ่มต้น 3%)
- **เวลารัน**: แก้ cron ใน `main.yml` (ค่าเริ่มต้น ทุก 12 ชม.)
- **ประเทศ/ภูมิภาค**: แก้ `PARAMS["country_code"]` ใน Python scraper
