import json
import os
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path

ARTIST_URL = "https://ticketdive.com/artist/OqOjl7jKnGct8rOG6KcO"
EVENTS_FILE = "events.json"
LINE_API_URL = "https://api.line.me/v2/bot/message/push"

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_USER_ID = os.environ["LINE_USER_ID"]


def fetch_events() -> list[dict]:
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(ARTIST_URL, headers=headers, timeout=15)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    events = []

    for a in soup.select("a[href^='/event/']"):
        title_el = a.select_one("h3")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)

        # リンク全体のテキストを取得して日付・会場を抽出
        full_text = a.get_text(separator="\n", strip=True)
        lines = [l.strip() for l in full_text.split("\n") if l.strip()]

        # 日付は "2026/XX/XX" の形式
        date = ""
        venue = ""
        for i, line in enumerate(lines):
            if re.match(r"\d{4}/\d{2}/\d{2}", line):
                date = line
                # 日付の次の行が会場
                if i + 1 < len(lines):
                    venue = lines[i + 1]
                break

        url = "https://ticketdive.com" + a["href"]
        events.append({"title": title, "date": date, "venue": venue, "url": url})

    return events


def load_previous_events() -> list[dict]:
    path = Path(EVENTS_FILE)
    if not path.exists():
        return []
    try:
        text = path.read_bytes().decode("utf-8-sig")
        return json.loads(text)
    except Exception:
        return []


def save_events(events: list[dict]):
    Path(EVENTS_FILE).write_text(
        json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def find_new_events(previous: list[dict], current: list[dict]) -> list[dict]:
    prev_urls = {e["url"] for e in previous}
    return [e for e in current if e["url"] not in prev_urls]


def send_line_message(new_events: list[dict]):
    lines = ["🎵 ChumToto に新しいイベントが追加されました！\n"]
    for e in new_events:
        lines.append(f"🎤 {e['title']}")
        if e.get("date"):
            lines.append(f"📅 {e['date']}")
        if e.get("venue"):
            lines.append(f"📍 {e['venue']}")
        lines.append(f"🔗 {e['url']}\n")

    message_text = "\n".join(lines).strip()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    }
    payload = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": message_text}],
    }
    res = requests.post(LINE_API_URL, headers=headers, json=payload, timeout=10)
    res.raise_for_status()
    print("LINE通知を送信しました。")


def main():
    print("イベントを取得中...")
    current = fetch_events()
    print(f"取得件数: {len(current)}")
    for e in current:
        print(e)

    previous = load_previous_events()
    new_events = find_new_events(previous, current)

    if new_events:
        print(f"新イベント {len(new_events)} 件を検出！")
        send_line_message(new_events)
    else:
        print("新しいイベントはありませんでした。")

    save_events(current)


if __name__ == "__main__":
    main()
