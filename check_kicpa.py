import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://www.kicpa.or.kr/home/jobOffrSrchNewGnrl/list.face"
STATE_FILE = "last_seen.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers, timeout=20)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

posts = []

# 게시판 행 단위로 읽기
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

    post_id = None

    # href 또는 onclick 안에서 게시글 ID 추출
    import re

    text_to_search = href + " " + onclick

    match = re.search(r"(\d{10,})", text_to_search)

    if match:
        post_id = match.group(1)

    if post_id:
        post_url = (
            "https://www.kicpa.or.kr"
            "/home/jobOffrSrchNewGnrl/detail.face"
            f"?ijIdNum={post_id}"
        )
    else:
        # ID를 못 잡아도 제목 기준으로 새 글 감지는 가능하게 처리
        post_url = title

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
    print("새로운 KICPA 수습CPA 채용공고가 있습니다!")

    for post in new_posts:
        print("제목:", post["title"])
        print("링크:", post["url"])

else:
    print("새로운 공고가 없습니다.")

with open(STATE_FILE, "w", encoding="utf-8") as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)
