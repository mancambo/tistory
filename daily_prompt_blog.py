# daily_prompt_blog.py
import time
import re
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from openai import OpenAI
from datetime import datetime
load_dotenv()  # .env 파일 로드
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# 1. 🔑 OpenAI API 키 설정
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 2. 🧠 GPT 프롬프트 꿀팁 글 생성 함수
def generate_prompt_tip_html():
    today = datetime.now().strftime("%Y년 %m월 %d일")

    system_msg = """
    너는 GPT 프롬프트 꿀팁을 매일 소개하는 프롬프트 엔지니어야.
    조회수 안 나오던 블로그 글이 GPT로 상위노출되는 스토리텔링 형식으로 글을 써.
    - 실패 경험 → 꿀팁 공개 → 변화 설명
    - 제목은 감정 유발 + 숫자 포함
    - 본문은 SEO 상위노출 구조
    - 마지막엔 CTA 문장 포함
    - 글은 HTML 태그로 구조화 (<h2>, <p>, <ul>, <strong> 등 사용)
    """

    user_msg = f"""
    오늘 소개할 GPT 프롬프트 주제를 하나 정하고, 그에 대한 꿀팁 블로그 글을 써줘.
    - 블로그 글 형식은 HTML로 <h2>, <p> 등 구조화
    - 마지막에 CTA 포함
    - 그리고 글 주제에 맞는 상위노출 가능한 연관 태그 5개도 리스트로 따로 뽑아줘
    - 예: ["GPT", "프롬프트", "블로그 자동화", "SEO", "상위노출"]
    날짜는 {today} 기준이야.
    """

    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]
    )

    content = res.choices[0].message.content

    # ✅ 태그 추출 (정규표현식으로 [ "GPT", "프롬프트", ... ] 형태만 추출)
    try:
        tag_match = re.search(r'\[[^\[\]]+\]', content)
        tag_str = tag_match.group() if tag_match else "[]"
        tags = eval(tag_str)
    except Exception as e:
        raise ValueError(f"[❌ GPT 응답 파싱 실패]\n{e}\n\n{content}")

    # ✅ 제목 추출
    try:
        title_match = re.search(r"\[제목\](.+)", content)
        title = title_match.group(1).strip() if title_match else "GPT 프롬프트 꿀팁"
    except:
        title = "GPT 프롬프트 꿀팁"

    # ✅ HTML 추출
    html = content.split("[본문]")[-1].split("[태그]")[0].strip()

    return title, html, tags

# ✅ 3. 티스토리 자동 업로드
def upload_to_tistory(title, html_content, tags):
    service = Service("D:/tistory/chromedriver.exe")

    options = webdriver.ChromeOptions()

    options.add_argument(r"user-data-dir=C:/Users/dogho/AppData/Local/Google/Chrome/User Data")
    options.add_argument("profile-directory=Default")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-features=TranslateUI")
    # options.add_argument("--headless")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://mancambo.tistory.com/manage/newpost")  # 티스토리 에디터 페이지로 수정 필요
    time.sleep(5)

    try:
        # 제목 입력
        driver.find_element(By.NAME, "title").send_keys(title)
        time.sleep(1)

        # 본문 입력
        driver.execute_script(f'document.querySelector(".se-editable").innerHTML = `{html_content}`;')
        time.sleep(1)

        # 카테고리 선택
        try:
            driver.find_element(By.ID, "category-btn").click()
            time.sleep(1)
            driver.find_element(By.XPATH, '//i[contains(text(), "프롬프트 실험실")]').click()
            time.sleep(1)
        except:
            print("⚠️ 카테고리 선택 실패")

        # 태그 입력
        try:
            driver.find_element(By.ID, "tagText").send_keys(", ".join(tags))
        except:
            print("⚠️ 태그 입력 실패")

        # 발행 버튼 클릭
        driver.find_element(By.ID, "publish-btn").click()
        print("✅ 블로그 글 발행 완료")

    except Exception as e:
        print(f"❌ 업로드 중 오류 발생: {e}")

    finally:
        time.sleep(3)
        driver.quit()

# ✅ 4. 실행 함수
def post_daily():
    title, html, tags = generate_prompt_tip_html()
    upload_to_tistory(title, html, tags)

# ✅ 5. 수동 실행
if __name__ == "__main__":
    post_daily()