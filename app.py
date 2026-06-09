import requests
import re
from flask import Flask, render_template, jsonify

app = Flask(__name__, template_folder='.', static_folder='.')

def format_view_count(count):
    if count is None:
        return None
    return f"{count/1000:.1f}K" if count >= 1000 else str(count)

def format_like_count(count):
    if count is None:
        return None
    return f"{count:,}개"

def parse_number(text):
    if not text:
        return None
    raw = text.replace(',', '').strip()
    return int(raw) if raw.isdigit() else None

def process_youtube_data(project):
    # 크롤링 제한이나 로딩 지연 시 들어갈 실제 기준 수치 예비 세팅
    if project["id"] == 1:
        project["views"] = "268회"
        project["likes"] = "1개"
    else:
        project["views"] = "897회"
        project["likes"] = "10개"
        
    project["img_url"] = f"https://img.youtube.com/vi/{project['youtube_id']}/maxresdefault.jpg"
    project["link"] = f"https://www.youtube.com/shorts/{project['youtube_id']}"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "ko-KR,ko;q=0.9"
        }
        response = requests.get(project["link"], headers=headers, timeout=5)
        if response.status_code == 200:
            page_source = response.text

            view_match = re.search(r'"viewCount"\s*:\s*"([\d,]+)"', page_source)
            if not view_match:
                view_match = re.search(r'"viewCountText"\s*:\s*\{\s*"simpleText"\s*:\s*"([\d,]+)\s*조회수"', page_source)

            if view_match:
                views_raw = parse_number(view_match.group(1))
                if views_raw is not None:
                    project["views"] = format_view_count(views_raw)

            like_match = re.search(r'"label"\s*:\s*"좋아요\s*([\d,]+)회"', page_source)
            if not like_match:
                like_match = re.search(r'좋아요\s*([\d,]+)회', page_source)

            if like_match:
                likes_raw = parse_number(like_match.group(1))
                if likes_raw is not None:
                    project["likes"] = format_like_count(likes_raw)
    except Exception as e:
        print(f"유튜브 데이터 수집 에러: {e}")

PORTFOLIO_DATA = {
    "creator_info": {
        "name": "정지윤",
        "title": "콘텐츠 크리에이터",
        "intro": "음악과 미학, 그리고 아날로그의 가치를 탐구하며 시각적 서사로 기록합니다."
    },
    "projects": [
        {
            "id": 1,
            "type": "shorts",
            "youtube_id": "72OD70BKlkk",
            "title": "🎵 부산 lp카페 뮤직 컴플렉스 소개",
            "subtitle": "아날로그 감성을 깨우는 최대 규모 LP 카페 청음기"
        },
        {
            "id": 2,
            "type": "shorts",
            "youtube_id": "cBDyfHAQ_Rk",
            "title": "🌸 부산 시민공원 봄 피크닉",
            "subtitle": "따스한 햇살과 바람, 봄의 미학을 담아낸 숏폼 필름"
        },
        {
            "id": 3,
            "type": "product",
            "img_url": "./IMG_9791.PNG",  # ⚠️ 정적 경로 상대 참조 기호(./) 명시화
            "title": "🎸 NFC 태그 기타피크 키링 소개 내용 및 이미지",
            "subtitle": "터치 한 번으로 나의 시그니처 플레이리스트를 연결하는 굿즈 디자인",
            "link": "https://github.com/"  # 누락되었던 굿즈 상세 아카이브 링크 반영
        },
        {
            "id": 4,
            "type": "web",
            "img_url": "./music.jpeg",  # ⚠️ 정적 경로 상대 참조 기호(./) 명시화 및 소문자 소스 통일
            "title": "💿 lp카페 뮤직 컴플렉스 내가 만든 사이트",
            "subtitle": "LP 샵의 강렬한 아이덴티티와 공간감을 웹 UI로 재해석한 아카이빙 사이트",
            "link": "https://fuzzymush.aiapp.help"  # 뮤직플랫폼 실제 방문 배포 주소
        }
    ]
}

def get_short_stats():
    stats = []
    for project in PORTFOLIO_DATA["projects"]:
        if project["type"] == "shorts":
            process_youtube_data(project)
            stats.append({
                "id": project["id"],
                "views": project["views"],
                "likes": project["likes"]
            })
    return stats

@app.route('/')
def home():
    get_short_stats()
    return render_template('index.html', data=PORTFOLIO_DATA)

def build_static_pages():
    print("🚀 GitHub Pages용 실시간 데이터 융합 정적 빌드 시작...")
    get_short_stats()
    with app.app_context():
        rendered_html = render_template('index.html', data=PORTFOLIO_DATA)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(rendered_html)
    print("✨ index.html 배포 파일 정밀 생성 완료!")

if __name__ == '__main__':
    build_static_pages()
    app.run(debug=True, port=5000)
    