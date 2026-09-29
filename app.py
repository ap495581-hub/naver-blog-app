import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="리치맘 R 블로그 도우미", page_icon="✍️", layout="centered")

# 사이드바: Gemini API Key만 입력
with st.sidebar:
    st.header("⚙️ 설정")
    gemini_key = st.text_input("Gemini API Key", type="password", help="Google AI Studio에서 무료 발급받은 키를 입력하세요.")

st.title("✍️ 리치맘 R 블로그 생성기")
st.caption("소재만 간단히 적으면 아내분의 평소 문체와 30개 해시태그가 완비된 원고를 생성합니다.")

category = st.selectbox("카테고리", ["육아용품/장난감", "맛집/카페", "나들이/여행/실내놀이", "생활용품/살림", "일상"])
item_name = st.text_input("제품명 또는 장소명", placeholder="예: 베어블리 자석레일 베이직")
sponsor = st.radio("유형", ["내돈내산", "체험단/협찬"], horizontal=True)
notes = st.text_area("핵심 경험 & 솔직 후기 메모", placeholder="아이 반응, 좋았던 점, 아쉬운 점, 꿀팁 등 생각나는 대로 입력", height=130)

if st.button("✨ 블로그 글 생성하기", type="primary", use_container_width=True):
    if not gemini_key:
        st.error("사이드바에 Gemini API Key를 먼저 입력해 주세요!")
    elif not item_name:
        st.error("제품명 또는 장소명을 입력해 주세요!")
    else:
        with st.spinner("아내분의 블로그 문체와 30개 해시태그를 반영하여 원고를 작성 중입니다..."):
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"""당신은 네이버 블로그 '리치맘 R'의 전담 작가입니다.
규칙:
1. 분량: 반드시 550자 이상의 풍성한 '긴 글' 형태
2. 제목: [핵심키워드]_부제목 (솔직 후기 등)
3. 소제목 앞 '✅' 이모지 필수 사용 (4~5개 단락 구성)
4. 문체: 다정하고 밝은 30대 육아맘 대화체 (~해요, ~더라고요, 강추강추해요 등)
5. 서식: 모바일 가독성 1~2문장 줄바꿈, [사진 1: ...], [형광펜 강조: "..."] 표기
6. 해시태그: 본문 맨 끝에 정확히 30개 공백 구분 출력 (#태그1 ... #태그30)

[소재 정보]
- 카테고리: {category}
- 이름: {item_name} ({sponsor})
- 메모: {notes}"""
                response = model.generate_content(prompt)
                st.session_state["post_text"] = response.text
                st.success("원고가 완성되었습니다! 아래에서 복사해 사용하세요.")
            except Exception as e:
                st.error(f"생성 실패: {str(e)}")

if "post_text" in st.session_state:
    full_text = st.session_state["post_text"]
    lines = full_text.strip().split("\n")
    title_text = lines[0].replace("#", "").strip()
    body_text = "\n".join(lines[1:]).strip()

    st.divider()
    st.subheader("📌 생성된 제목")
    st.code(title_text, language="text")

    st.subheader("📝 생성된 본문 & 해시태그 (30개)")
    st.code(body_text, language="text")

    st.markdown("""
    <a href="https://m.blog.naver.com" target="_blank" style="display: block; text-align: center; background-color: #03C75A; color: white; padding: 12px; border-radius: 8px; font-weight: bold; text-decoration: none; margin-top: 15px;">
        🚀 네이버 블로그 바로가기
    </a>
    """, unsafe_allow_html=True)
