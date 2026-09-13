import requests
from bs4 import BeautifulSoup
import json
import os
import re

URL = "https://www.kicpa.or.kr/home/jobOffrSrchNewGnrl/list.face"
STATE_FILE = "last_seen.json"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

headers = {
    "User-Agent": "Mozilla/5.0"
}

def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("텔레그램 설정이 없습니다.")
        return

    telegram_url = (
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    response = requests.post(
        telegram_url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        },
        timeout=20
    )

    response.raise_for_status()


response = requests.get(URL, headers=headers, timeout=20)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

posts = []

for row in soup.find_all("tr"):
    cells = row.find_all("td")

    if len(cells) < 2:
        continue

    title_cell = cells[1]
    title = title_cell.get_text(" ", strip=True)

    if not title:
        continue

    link = title_cell.find("a")

    if not link:
        continue

    href = link.get("href", "")
    onclick = link.get("onclick", "")

    match = re.search(r"(\d{10,})", href + " " + onclick)

    if match:
        post_id = match.group(1)
        post_url = (
            "https://www.kicpa.or.kr"
            "/home/jobOffrSrchNewGnrl/detail.face"
            f"?ijIdNum={post_id}"
        )
    else:
        post_url = URL

    posts.append({
        "title": title,
        "url": post_url
    })

print(f"현재 게시글 {len(posts)}개 감지")

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        previous = json.load(f)
else:
    previous = []

previous_keys = {
    (p["title"], p["url"])
    for p in previous
}

new_posts = [
    p for p in posts
    if (p["title"], p["url"]) not in previous_keys
]

if not previous:
    print("첫 실행입니다. 현재 게시글을 기준점으로 저장합니다.")

elif new_posts:
    print(f"새로운 공고 {len(new_posts)}개 발견")

    for post in new_posts:
        message = (
            "🔔 KICPA 신규 수습CPA 공고\n\n"
            f"{post['title']}\n\n"
            f"{post['url']}"
        )

        send_telegram(message)

else:
    print("새로운 공고가 없습니다.")

with open(STATE_FILE, "w", encoding="utf-8") as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)
    send_telegram("🔔 KICPA 알림 테스트 성공!")
