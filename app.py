import streamlit as st
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import google.generativeai as genai

st.set_page_config(page_title="리치맘 R 블로그 생성기", page_icon="✍️")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 기본 설정")
    gemini_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    st.subheader("네이버 메일 설정")
    naver_id = st.text_input("네이버 아이디 (아이디만 입력)")
    naver_pw = st.text_input("네이버 비밀번호 (애플리케이션 비밀번호)", type="password")
    blog_id = st.text_input("블로그 아이디 (보통 네이버 아이디와 동일)")

st.title("✍️ 리치맘 R 블로그 초안 생성기")

# 입력 폼
category = st.selectbox("카테고리", ["육아용품/장난감", "맛집/카페", "나들이/여행", "일상/살림"])
item_name = st.text_input("제품명 / 장소명", placeholder="예: 베어블리 자석레일 베이직")
sponsor = st.radio("유형", ["내돈내산", "체험단 협찬"], horizontal=True)
notes = st.text_area("핵심 경험 & 후기 메모", placeholder="아이 반응, 장단점 등 자유롭게 입력", height=120)
uploaded_files = st.file_uploader("포스팅 사진 첨부", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if st.button("✨ 블로그 글 생성 및 자동 발행", type="primary"):
    if not gemini_key or not naver_id or not naver_pw or not item_name:
        st.error("사이드바 설정과 제품명을 모두 입력해 주세요!")
    else:
        with st.spinner("아내분 문체와 30개 해시태그를 반영하여 글을 작성 중입니다..."):
            try:
                # 1. Gemini로 원고 생성
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"""당신은 네이버 블로그 '리치맘 R'의 전담 작가입니다.
규칙:
1. 분량: 반드시 550자 이상의 풍성한 '긴 글' 형태
2. 제목: [핵심키워드]_부제목 (솔직 후기 등)
3. 소제목 앞 '✅' 이모지 필수 사용 (4~5개 단락 구성)
4. 문체: 다정하고 밝은 30대 육아맘 대화체 (~해요, ~더라고요, 강추강추해요 등)
5. 서식: 모바일 가독성 1~2문장 줄바꿈, [형광펜 강조: "..."] 표기
6. 해시태그: 본문 맨 끝에 정확히 30개 공백 구분 출력 (#태그1 ... #태그30)

[소재 정보]
- 카테고리: {category}
- 이름: {item_name} ({sponsor})
- 메모: {notes}"""
                response = model.generate_content(prompt)
                post_text = response.text
                
                # 2. 네이버 블로그 이메일 전송
                target_blog = blog_id if blog_id else naver_id
                recipient = f"{target_blog}@blog.naver.com"
                sender = f"{naver_id}@naver.com"
                
                # 제목 추출 (첫 줄)
                lines = post_text.strip().split("\n")
                subject = f"[비공개] {lines[0].replace('#', '').strip()}"
                
                msg = MIMEMultipart("related")
                msg["From"] = sender
                msg["To"] = recipient
                msg["Subject"] = subject
                
                # HTML 본문 변환
                html_body = f"<pre style='font-family: sans-serif; font-size: 16px; white-space: pre-wrap; line-height: 1.8;'>{post_text}</pre>"
                msg.attach(MIMEText(html_body, "html", "utf-8"))
                
                # 사진 첨부
                if uploaded_files:
                    for uf in uploaded_files:
                        img = MIMEImage(uf.read(), name=uf.name)
                        img.add_header("Content-Disposition", "attachment", filename=uf.name)
                        msg.attach(img)
                
                with smtplib.SMTP_SSL("smtp.naver.com", 465) as server:
                    server.login(naver_id, naver_pw)
                    server.sendmail(sender, recipient, msg.as_string())
                    
                st.success("🎉 글 생성 및 네이버 블로그([비공개] 초안) 등록이 완료되었습니다!")
                st.text_area("생성된 글 확인", post_text, height=300)
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
