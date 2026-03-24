"""GitHub Actions用: Google Sheets → CSV エクスポート（環境変数から認証）"""
import sys
import io
import os
import csv
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
OUTPUT = Path(__file__).parent / "data" / "engagement.csv"


def export() -> None:
    sa_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not sa_json:
        print("[NG] GOOGLE_SERVICE_ACCOUNT_JSON not set")
        sys.exit(1)

    spreadsheet_id = os.environ.get("SPREADSHEET_ID")
    if not spreadsheet_id:
        print("[NG] SPREADSHEET_ID not set")
        sys.exit(1)

    info = json.loads(sa_json)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    gc = gspread.authorize(creds)

    sheet = gc.open_by_key(spreadsheet_id).worksheet("投稿管理")
    records = sheet.get_all_records()

    published = [
        r for r in records
        if r.get("status") == "published" and r.get("impressions_5h")
    ]

    if not published:
        print("[NG] No published records with engagement data")
        sys.exit(1)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    keys = [
        "post_id", "title", "content", "x_axis", "y_axis",
        "status", "tweet_id", "tweet_url",
        "hook_type", "emotional_appeal", "tone", "uses_numbers",
        "character_count", "sentiment_score", "time_band", "day_of_week",
        "likes_5h", "retweets_5h", "impressions_5h",
        "post_source",
        "quote_source_username", "quote_source_followers", "quote_link_type",
    ]

    with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(published)

    print(f"[OK] {len(published)} records exported to {OUTPUT}")


if __name__ == "__main__":
    export()
