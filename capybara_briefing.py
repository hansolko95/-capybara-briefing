import os
import requests
from datetime import datetime

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_PAGE_ID = os.environ["NOTION_PAGE_ID"]


def get_news_briefing():
    today = datetime.now().strftime("%Y년 %m월 %d일")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    prompt = f"""오늘은 {today}입니다.
당신은 "카피바라 특파원"이라는 귀엽고 친근한 캐릭터입니다. 🦫
오늘의 한국 및 글로벌 경제/주식 주요 뉴스 4가지를 브리핑해주세요.

각 뉴스는 아래 형식으로 작성해주세요:
- 카테고리 (예: 코스피, 환율, 미국증시, 원자재 등)
- 뉴스 제목
- 2~3문장 요약 (카피바라 특파원답게 친근하고 재밌게!)
- 시장 방향: 상승 / 하락 / 중립 중 하나

마지막에 오늘의 한 줄 총평도 카피바라 스타일로 추가해주세요."""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1500}
    }
    res = requests.post(url, json=payload)
    res.raise_for_status()
    data = res.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def get_notion_headers():
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }


def add_briefing_to_notion(briefing_text):
    today = datetime.now().strftime("%Y년 %m월 %d일")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    paragraphs = [p.strip() for p in briefing_text.strip().split("\n") if p.strip()]

    children = []
    children.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": f"🦫 {today} 카피바라 특파원 브리핑"}}]
        }
    })
    children.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": f"📅 발행: {now_str}"}, "annotations": {"color": "gray"}}]
        }
    })
    children.append({"object": "block", "type": "divider", "divider": {}})

    for para in paragraphs:
        if para.startswith("**") or para.startswith("##"):
            para = para.replace("**", "").replace("##", "").strip()
            children.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"type": "text", "text": {"content": para}}],
                    "icon": {"emoji": "📰"}
                }
            })
        else:
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": para}}]
                }
            })

    children.append({"object": "block", "type": "divider", "divider": {}})

    url = f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children"
    res = requests.patch(url, headers=get_notion_headers(), json={"children": children})
    res.raise_for_status()
    print(f"✅ 노션 업데이트 완료! ({now_str})")


def main():
    print("🦫 카피바라 특파원 브리핑 시작...")
    briefing = get_news_briefing()
    print("📰 뉴스 요약 완료!")
    print(briefing)
    print("\n노션에 업로드 중...")
    add_briefing_to_notion(briefing)
    print("🎉 완료!")


if __name__ == "__main__":
    main()
