import base64
import random
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="THE DINING TABLE",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "kitchen_home.png"
VALID_PAGES = {"home", "nutrition", "meal", "farm", "bmi"}

# -----------------------------
# 페이지 및 세션 상태
# -----------------------------
query_page = st.query_params.get("page")
if query_page in VALID_PAGES:
    st.session_state.page = query_page
elif "page" not in st.session_state or st.session_state.page not in VALID_PAGES:
    st.session_state.page = "home"

if "intake" not in st.session_state:
    st.session_state.intake = []
if "suggestion" not in st.session_state:
    st.session_state.suggestion = ""


def set_page(page: str):
    if page not in VALID_PAGES:
        page = "home"
    st.session_state.page = page
    st.query_params["page"] = page


def back_home():
    set_page("home")


# -----------------------------
# 디자인: 한글 고딕 + 영문 Cormorant Garamond
# 사이드바에도 글꼴이 덮어써지지 않도록 선택자를 분리
# -----------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

:root {
    --bg: #171310;
    --panel: #241d17;
    --gold: #c8a66b;
    --line: #59452f;
    --text: #eee6da;
    --muted: #b9a995;
}

html, body, [class*="css"], button, input, textarea, select,
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] {
    font-family: 'Noto Sans KR', sans-serif !important;
}
body, p, li, label, input, textarea, select, button,
[data-testid="stWidgetLabel"] { letter-spacing: -0.01em; }
.stApp { background: var(--bg); color: var(--text); }
[data-testid="stHeader"] { background: rgba(23,19,16,.92); }
.block-container { max-width: 1180px; padding-top: 1.2rem; padding-bottom: 2.5rem; }

h1, h2, h3, h4, h5, h6 {
    font-family: 'Noto Sans KR', sans-serif !important;
    color: #f1e5d3 !important;
    font-weight: 600 !important;
}
.brand, .kicker, .english-menu, .english-title, .sidebar-brand,
.sidebar-kicker, .sidebar-section-label, .footer-brand {
    font-family: 'Cormorant Garamond', serif !important;
}
.brand { font-size: clamp(2rem, 4vw, 3.1rem); letter-spacing: .12em; line-height: 1.1; color: #f1e5d3; }
.kicker { color: var(--gold); font-size: .85rem; letter-spacing: .2em; margin-top: .45rem; }
p, li, label, [data-testid="stWidgetLabel"] { color: var(--text); }
a { color: #e0c28c !important; }

/* Sidebar: 브랜드와 영문 문구는 항상 Cormorant Garamond */
[data-testid="stSidebar"] { background: #201914; border-right: 1px solid var(--line); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { font-family: 'Noto Sans KR', sans-serif !important; }
[data-testid="stSidebar"] .sidebar-brand,
[data-testid="stSidebar"] .sidebar-kicker,
[data-testid="stSidebar"] .sidebar-section-label,
[data-testid="stSidebar"] .english-menu {
    font-family: 'Cormorant Garamond', serif !important;
}
[data-testid="stSidebar"] .sidebar-brand { font-size: 1.55rem; letter-spacing: .06em; color: #f1e5d3; }
[data-testid="stSidebar"] .sidebar-kicker { color: var(--gold); letter-spacing: .1em; font-size: .83rem; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 { color: #f1e5d3 !important; }

/* 버튼: 평소에는 차분하게, 마우스를 올리면 선택 영역이 분명하게 보임 */
div.stButton > button, [data-testid="stLinkButton"] a {
    width: 100%; min-height: 2.8rem; border: 1px solid var(--line);
    border-radius: 4px; background: var(--panel); color: #f0e4d2;
    transition: background .18s ease, border-color .18s ease, transform .18s ease, box-shadow .18s ease;
}
div.stButton > button:hover, [data-testid="stLinkButton"] a:hover {
    border-color: var(--gold) !important; background: #392b1f !important;
    color: #fff2d8 !important; box-shadow: 0 0 0 1px rgba(200,166,107,.22);
    transform: translateY(-1px);
}
div.stButton > button:focus-visible { outline: 2px solid var(--gold) !important; outline-offset: 2px; }
[data-testid="stMetric"] { background: var(--panel); border: 1px solid var(--line); border-radius: 4px; padding: .7rem; }
[data-testid="stMetricLabel"] { color: var(--muted) !important; }
hr { border-color: var(--line) !important; }
footer { visibility: hidden; }

/* 홈의 클릭 가능한 이미지 영역 */
.kitchen-shell { position: relative; width: 100%; overflow: hidden; border: 1px solid var(--line); border-radius: 5px; background: #211a15; }
.kitchen-shell img { display: block; width: 100%; height: auto; }
.kitchen-hotspot {
    position: absolute; display: flex; align-items: center; justify-content: center;
    text-align: center; text-decoration: none !important; color: #fff5e5 !important;
    border: 1px solid transparent; border-radius: 8px; background: rgba(23,19,16,0);
    transition: background .18s ease, border-color .18s ease, box-shadow .18s ease;
    min-width: 9%; min-height: 12%; padding: .45rem;
}
.kitchen-hotspot span { opacity: 0; transform: translateY(4px); transition: opacity .18s ease, transform .18s ease; font-family: 'Noto Sans KR', sans-serif; font-size: clamp(.7rem, 1.1vw, .95rem); font-weight: 600; text-shadow: 0 1px 4px #000; }
.kitchen-hotspot:hover, .kitchen-hotspot:focus-visible { background: rgba(23,19,16,.76); border-color: var(--gold); box-shadow: 0 0 0 2px rgba(200,166,107,.2); outline: none; }
.kitchen-hotspot:hover span, .kitchen-hotspot:focus-visible span { opacity: 1; transform: translateY(0); }
.hotspot-nutrition { left: 5%; top: 28%; width: 20%; height: 45%; }
.hotspot-meal { left: 31%; top: 53%; width: 27%; height: 34%; }
.hotspot-bmi { left: 57%; top: 25%; width: 19%; height: 48%; }
.hotspot-farm { right: 3%; top: 20%; width: 17%; height: 38%; }
.home-hint { color: var(--muted); font-size: .9rem; margin-top: .65rem; }
.footer-brand { text-align: center; color: #9e8d79; letter-spacing: .15em; font-size: .9rem; }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# 예시 식품 데이터
# -----------------------------
FOODS = {
    "닭가슴살 100g": {"kcal": 165, "탄수화물(g)": 0, "단백질(g)": 31, "지방(g)": 3.6, "나트륨(mg)": 74, "serving": "100g"},
    "달걀 1개": {"kcal": 72, "탄수화물(g)": 0.4, "단백질(g)": 6.3, "지방(g)": 4.8, "나트륨(mg)": 71, "serving": "1개"},
    "흰쌀밥 1공기": {"kcal": 300, "탄수화물(g)": 66, "단백질(g)": 5.5, "지방(g)": 0.6, "나트륨(mg)": 5, "serving": "약 210g"},
    "고구마 100g": {"kcal": 130, "탄수화물(g)": 31, "단백질(g)": 1.5, "지방(g)": 0.2, "나트륨(mg)": 15, "serving": "100g"},
    "바나나 1개": {"kcal": 105, "탄수화물(g)": 27, "단백질(g)": 1.3, "지방(g)": 0.4, "나트륨(mg)": 1, "serving": "중간 크기 1개"},
    "사과 1개": {"kcal": 95, "탄수화물(g)": 25, "단백질(g)": 0.5, "지방(g)": 0.3, "나트륨(mg)": 2, "serving": "중간 크기 1개"},
    "두부 100g": {"kcal": 76, "탄수화물(g)": 1.9, "단백질(g)": 8, "지방(g)": 4.8, "나트륨(mg)": 7, "serving": "100g"},
    "연어 100g": {"kcal": 208, "탄수화물(g)": 0, "단백질(g)": 20, "지방(g)": 13, "나트륨(mg)": 59, "serving": "100g"},
    "그릭요거트 100g": {"kcal": 97, "탄수화물(g)": 3.9, "단백질(g)": 9, "지방(g)": 5, "나트륨(mg)": 36, "serving": "100g"},
    "아몬드 10알": {"kcal": 70, "탄수화물(g)": 2.6, "단백질(g)": 2.6, "지방(g)": 6.1, "나트륨(mg)": 0, "serving": "약 12g"},
    "브로콜리 100g": {"kcal": 34, "탄수화물(g)": 6.6, "단백질(g)": 2.8, "지방(g)": 0.4, "나트륨(mg)": 33, "serving": "100g"},
    "우유 200ml": {"kcal": 122, "탄수화물(g)": 9.6, "단백질(g)": 6.4, "지방(g)": 6.8, "나트륨(mg)": 86, "serving": "200ml"},
    "김치 50g": {"kcal": 10, "탄수화물(g)": 1.8, "단백질(g)": 0.7, "지방(g)": 0.2, "나트륨(mg)": 250, "serving": "50g"},
    "샐러드 1그릇": {"kcal": 80, "탄수화물(g)": 12, "단백질(g)": 3, "지방(g)": 3, "나트륨(mg)": 120, "serving": "채소 약 150g"},
}

RECIPES = {
    "연어 곡물 볼": ["연어 100g", "흰쌀밥 1공기", "브로콜리 100g"],
    "닭가슴살 샐러드": ["닭가슴살 100g", "샐러드 1그릇", "달걀 1개"],
    "두부 채소 덮밥": ["두부 100g", "흰쌀밥 1공기", "브로콜리 100g"],
    "고구마와 그릭요거트": ["고구마 100g", "그릭요거트 100g", "아몬드 10알"],
    "간단한 아침 식사": ["달걀 1개", "바나나 1개", "우유 200ml"],
    "균형 잡힌 한식 한 끼": ["흰쌀밥 1공기", "닭가슴살 100g", "브로콜리 100g", "김치 50g"],
    "연어 샐러드 플레이트": ["연어 100g", "샐러드 1그릇", "고구마 100g"],
    "두부 단백질 플레이트": ["두부 100g", "달걀 1개", "샐러드 1그릇"],
}
NUTRIENTS = ["kcal", "탄수화물(g)", "단백질(g)", "지방(g)", "나트륨(mg)"]
LABELS = ["열량 (kcal)", "탄수화물 (g)", "단백질 (g)", "지방 (g)", "나트륨 (mg)"]


def total_foods(names):
    totals = {key: 0.0 for key in NUTRIENTS}
    for name in names:
        for key in NUTRIENTS:
            totals[key] += FOODS[name][key]
    return totals


def show_nutrients(values):
    cols = st.columns(5)
    for col, key, label in zip(cols, NUTRIENTS, LABELS):
        col.metric(label, f"{values[key]:.1f}")


# -----------------------------
# 사이드바
# -----------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-brand">THE DINING TABLE</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-kicker">FOOD · NUTRITION · SUSTAINABILITY</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="sidebar-section-label">Explore</div>', unsafe_allow_html=True)
    nav_items = [
        ("🏠 홈으로", "home", "nav_home"),
        ("🥗 영양 성분 분석", "nutrition", "nav_nutrition"),
        ("🍱 맞춤형 식단", "meal", "nav_meal"),
        ("🌱 스마트팜 검색", "farm", "nav_farm"),
        ("📊 BMI 안내", "bmi", "nav_bmi"),
    ]
    for label, page, key in nav_items:
        if st.button(label, use_container_width=True, key=key, type="secondary"):
            set_page(page)
            st.rerun()
    st.divider()
    st.caption("메뉴를 선택하면 해당 기능 화면으로 이동합니다.")

# -----------------------------
# 공통 헤더
# -----------------------------
st.markdown(
    '<div class="brand">THE DINING TABLE</div>'
    '<div class="kicker">FOOD · NUTRITION · A BETTER YOU</div><hr>',
    unsafe_allow_html=True,
)

# -----------------------------
# 홈 화면: 이미지 위에 마우스를 올리면 기능 라벨 표시 및 클릭 가능
# -----------------------------
if st.session_state.page == "home":
    if IMAGE_PATH.exists():
        image_data = base64.b64encode(IMAGE_PATH.read_bytes()).decode("utf-8")
        suffix = IMAGE_PATH.suffix.lower()
        mime = "image/png" if suffix == ".png" else "image/jpeg"
        st.markdown(
            f"""<div class="kitchen-shell">
              <img src="data:{mime};base64,{image_data}" alt="주방 메인 화면" />
              <a class="kitchen-hotspot hotspot-nutrition" href="?page=nutrition" target="_top" aria-label="영양 성분 분석"><span>🥗 영양 성분 분석</span></a>
              <a class="kitchen-hotspot hotspot-meal" href="?page=meal" target="_top" aria-label="맞춤형 식단"><span>🍱 맞춤형 식단</span></a>
              <a class="kitchen-hotspot hotspot-bmi" href="?page=bmi" target="_top" aria-label="BMI 안내"><span>📊 BMI 안내</span></a>
              <a class="kitchen-hotspot hotspot-farm" href="?page=farm" target="_top" aria-label="스마트팜 검색"><span>🌱 스마트팜 검색</span></a>
            </div>""",
            unsafe_allow_html=True,
        )
        st.markdown('<div class="home-hint">주방 그림 속 냉장고·식탁·사람·식물 영역에 마우스를 올려 기능을 확인하고 클릭하세요.</div>', unsafe_allow_html=True)
    else:
        st.warning("kitchen_home.png 파일이 없습니다. main.py와 같은 GitHub 저장소 폴더에 업로드해 주세요.")
        st.info("아래 기능 버튼을 눌러 원하는 화면으로 이동할 수 있습니다.")
        cols = st.columns(4)
        for col, (label, page, key) in zip(cols, nav_items[1:]):
            with col:
                if st.button(label, key=f"home_{key}", use_container_width=True):
                    set_page(page)
                    st.rerun()

    st.markdown('<div class="kicker">A THOUGHTFUL WAY TO EAT</div>', unsafe_allow_html=True)
    st.markdown("## Discover your table.")
    st.write("식품 영양 정보부터 맞춤형 식단, 지속 가능한 먹거리까지 한곳에서 확인하세요.")
    st.caption("이미지 위의 기능 영역 또는 왼쪽 메뉴를 이용할 수 있습니다.")

# -----------------------------
# 영양 성분 분석
# -----------------------------
elif st.session_state.page == "nutrition":
    if st.button("← 홈으로 돌아가기", key="nutrition_back"):
        back_home()
        st.rerun()
    st.header("Nutrition Check")
    st.write("식품을 선택해 영양 성분을 확인하고 섭취 기록을 관리하세요.")
    food = st.selectbox("식품 선택", list(FOODS.keys()))
    qty = st.number_input("섭취 단위 수", min_value=0.25, max_value=20.0, value=1.0, step=0.25)
    info = FOODS[food]
    show_nutrients({key: info[key] * qty for key in NUTRIENTS})
    st.caption(f"기준 제공량: {info['serving']} · 선택 수량: {qty:g}")
    if st.button("오늘 섭취 기록에 추가", key="add_intake"):
        st.session_state.intake.append({"식품": food, "수량": qty, **{key: info[key] * qty for key in NUTRIENTS}})
        st.success("오늘 섭취 기록에 추가했습니다.")
    if st.session_state.intake:
        st.subheader("오늘의 섭취 기록")
        df = pd.DataFrame(st.session_state.intake)
        st.dataframe(df, use_container_width=True, hide_index=True)
        show_nutrients({key: float(df[key].sum()) for key in NUTRIENTS})
        if st.button("오늘 기록 초기화", key="clear_intake"):
            st.session_state.intake = []
            st.rerun()
    st.caption("내장된 예시 데이터입니다. 정확한 수치는 제품 표시와 공식 식품 영양 데이터베이스를 확인하세요.")

# -----------------------------
# 맞춤형 식단
# -----------------------------
elif st.session_state.page == "meal":
    if st.button("← 홈으로 돌아가기", key="meal_back"):
        back_home()
        st.rerun()
    st.header("Meal Planner")
    st.write("메뉴를 선택해 식단 구성과 예상 영양 정보를 확인하세요.")
    recipe = st.selectbox("식단 메뉴 선택", list(RECIPES.keys()))
    st.subheader(recipe)
    st.write("구성 식품: " + " · ".join(RECIPES[recipe]))
    show_nutrients(total_foods(RECIPES[recipe]))
    if st.button("다른 메뉴 추천받기", key="recommend_recipe"):
        st.session_state.suggestion = random.choice([name for name in RECIPES if name != recipe])
    if st.session_state.suggestion:
        suggested = st.session_state.suggestion
        st.markdown(f"### 추천 메뉴: {suggested}")
        st.write("구성 식품: " + " · ".join(RECIPES[suggested]))
        show_nutrients(total_foods(RECIPES[suggested]))
    st.caption("식단 영양값은 식품별 예시 데이터를 합산한 추정치입니다.")

# -----------------------------
# 스마트팜 및 친환경 먹거리 검색
# -----------------------------
elif st.session_state.page == "farm":
    if st.button("← 홈으로 돌아가기", key="farm_back"):
        back_home()
        st.rerun()
    st.header("Smart Farm & Sustainable Food")
    st.write("지역과 검색 대상을 선택해 네이버 지도에서 관련 업체를 찾아보세요.")
    region = st.text_input("지역 입력", placeholder="예: 청주시 흥덕구")
    category = st.selectbox("검색 대상", ["스마트팜 기업", "스마트팜 체험농장", "친환경 채소 판매처", "로컬푸드 직매장"])
    if st.button("네이버 지도에서 검색", key="search_naver_map"):
        if not region.strip():
            st.warning("지역을 먼저 입력해주세요.")
        else:
            url = "https://map.naver.com/p/search/" + quote_plus(f"{region.strip()} {category}")
            st.link_button("네이버 지도 열기", url, use_container_width=True)
    st.caption("검색 결과의 주소, 영업 여부, 재배 방식은 업체 정보를 통해 다시 확인하세요.")

# -----------------------------
# BMI 안내
# -----------------------------
elif st.session_state.page == "bmi":
    if st.button("← 홈으로 돌아가기", key="bmi_back"):
        back_home()
        st.rerun()
    st.header("BMI Guide")
    st.write("BMI는 체중 상태를 단독으로 판단하는 기준이 아닙니다. 청소년은 성장 단계와 연령·성별별 기준을 함께 고려해야 합니다.")
    weight = st.number_input("체중 (kg)", min_value=1.0, max_value=300.0, value=60.0, step=0.5)
    height = st.number_input("키 (cm)", min_value=50.0, max_value=230.0, value=165.0, step=0.5)
    if st.button("BMI 계산", key="calculate_bmi"):
        bmi = weight / ((height / 100) ** 2)
        st.metric("계산된 BMI", f"{bmi:.1f}")
        st.info("청소년은 성인 BMI 분류를 그대로 적용하지 말고 연령·성별 성장도표와 공식 보건 자료를 확인하세요.")

# -----------------------------
# 하단
# -----------------------------
st.markdown("---")
st.markdown(
    '<div class="footer-brand">THE DINING TABLE · FOOD / NUTRITION / SUSTAINABILITY</div>',
    unsafe_allow_html=True,
)
