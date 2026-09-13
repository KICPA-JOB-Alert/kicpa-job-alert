import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://www.kicpa.or.kr/home/jobOffrSrchNewGnrl/list.face?ijEmpSep=all&listCnt=20"
STATE_FILE = "last_seen.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers, timeout=20)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# 게시판의 상세 글 링크 찾기
links = soup.find_all("a", href=True)

posts = []

for link in links:
    href = link.get("href", "")
    title = link.get_text(" ", strip=True)

    if "jobOffrSrchNewGnrl/detail.face" in href and title:
        if href.startswith("http"):
            post_url = href
        else:
            post_url = "https://www.kicpa.or.kr" + href

        posts.append({
            "title": title,
            "url": post_url
        })

# 중복 제거
unique_posts = []
seen_urls = set()

for post in posts:
    if post["url"] not in seen_urls:
        seen_urls.add(post["url"])
        unique_posts.append(post)

posts = unique_posts

print(f"현재 게시글 {len(posts)}개 감지")

# 이전 실행 기록 불러오기
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        previous = json.load(f)
else:
    previous = []

previous_urls = {p["url"] for p in previous}

new_posts = [
    p for p in posts
    if p["url"] not in previous_urls
]

if not previous:
    print("첫 실행입니다. 현재 게시글을 기준점으로 저장합니다.")

elif new_posts:
    print("새로운 KICPA 수습CPA 채용공고가 있습니다!")

    for post in new_posts:
        print(post["title"])
        print(post["url"])

else:
    print("새로운 공고가 없습니다.")

# 현재 상태 저장
with open(STATE_FILE, "w", encoding="utf-8") as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)
