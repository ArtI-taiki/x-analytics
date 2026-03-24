"""Google Sheets からエンゲージメントデータを CSV にエクスポートする"""
import sys
import io
import csv
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# credential_manager は x_content_system 側のものを利用
sys.path.insert(0, str(Path(__file__).parent.parent / "iCloudDrive" / "iCloud~md~obsidian" / "Obsidian" / "x_content_system"))

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
OUTPUT = Path(__file__).parent / "data" / "engagement.csv"


def load_credential(key: str) -> str | None:
    """DPAPI credential_manager から値を取得する"""
    try:
        from credential_manager import load_credential as _load
        return _load(key)
    except Exception:
        return None


def export() -> None:
    # 認証
    sa_json = load_credential("GOOGLE_SERVICE_ACCOUNT_JSON")
    if sa_json:
        info = json.loads(sa_json)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        sa_file = load_credential("GOOGLE_SERVICE_ACCOUNT_FILE") or "service_account.json"
        sa_path = Path(sa_file)
        if not sa_path.is_absolute():
            sa_path = Path(__file__).parent.parent / "iCloudDrive" / "iCloud~md~obsidian" / "Obsidian" / "x_content_system" / sa_file
        creds = Credentials.from_service_account_file(str(sa_path), scopes=SCOPES)

    gc = gspread.authorize(creds)
    spreadsheet_id = "1DV9TIey6e8Ko5qmEEigb3c2a4iropCtxNCkjLsfFKkI"

    sheet = gc.open_by_key(spreadsheet_id).worksheet("投稿管理")
    records = sheet.get_all_records()

    # published かつ impressions_5h がある行のみ
    published = [
        r for r in records
        if r.get("status") == "published" and r.get("impressions_5h")
    ]

    if not published:
        print("[NG] No published records with engagement data")
        sys.exit(1)

    # CSV 出力
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
