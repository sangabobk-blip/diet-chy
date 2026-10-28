
import streamlit as st
import pandas as pd
from pathlib import Path
from urllib.parse import quote_plus
import random

st.set_page_config(
    page_title="THE DINING TABLE",
    page_icon="🍽️",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "kitchen_home.png"

# -----------------------------
# 페이지 및 세션 상태 초기화
# -----------------------------
VALID_PAGES = {"home", "nutrition", "meal", "farm", "bmi"}

requested_page = st.query_params.get("page", "home")
if requested_page not in VALID_PAGES:
    requested_page = "home"
st.session_state.page = requested_page

if "intake" not in st.session_state:
    st.session_state.intake = []
if "suggestion" not in st.session_state:
    st.session_state.suggestion = ""

def set_page(page):
    if page not in VALID_PAGES:
        page = "home"
    st.session_state.page = page
    st.query_params["page"] = page

def back_home():
    set_page("home")

# -----------------------------
# 디자인: 전체 고딕체 통일
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #171310;
    --gold: #c8a66b;
    --line: #59452f;
    --text: #eee6da;
}

html, body, [class*="css"], button, input, textarea, select,
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] {
    font-family: 'Noto Sans KR', sans-serif !important;
}

.stApp {
    background: var(--bg);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: rgba(23,19,16,.92);
}

.block-container {
    max-width: 1180px;
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

h1, h2, h3, h4, h5, h6, .brand, .kicker,
[data-testid="stSidebar"] * {
    font-family: 'Noto Sans KR', sans-serif !important;
}

h1, h2, h3, h4, h5, h6 {
    color: #f1e5d3 !important;
    font-weight: 700 !important;
}

.brand {
    font-size: clamp(1.8rem, 3.5vw, 2.8rem);
    font-weight: 700;
    letter-spacing: .08em;
    line-height: 1.2;
    color: #f1e5d3;
}

.kicker {
    color: var(--gold);
    font-size: .8rem;
    font-weight: 600;
    letter-spacing: .12em;
}

p, li, label, [data-testid="stWidgetLabel"] {
    color: var(--text);
}

a {
    color: #e0c28c !important;
}

div.stButton > button, [data-testid="stLinkButton"] a {
    width: 100%;
    min-height: 2.8rem;
    border: 1px solid #59452f;
    border-radius: 5px;
    background: #241d17;
    color: #f0e4d2 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    transition: all .2s ease;
}

div.stButton > button:hover, [data-testid="stLinkButton"] a:hover {
    border-color: var(--gold);
    background: #30251c;
    color: #fff2d8 !important;
}

[data-testid="stMetric"] {
    background: #241d17;
    border: 1px solid var(--line);
    border-radius: 4px;
    padding: .7rem;
}

[data-testid="stSidebar"] {
    background: #201914;
    border-right: 1px solid #59452f;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
    color: #f1e5d3 !important;
}

hr {
    border-color: var(--line) !important;
}

footer {
    visibility: hidden;
}

/* 주방 이미지 위의 메뉴는 기본적으로 숨기고, 이미지에 마우스를 올렸을 때 표시 */
.kitchen-hotspot-wrap {
    position: relative;
    width: 100%;
    overflow: hidden;
    border-radius: 10px;
    line-height: 0;
    isolation: isolate;
}
.kitchen-hotspot-wrap img {
    display: block;
    width: 100%;
    height: auto;
}
.kitchen-hover-shade {
    position: absolute;
    inset: 0;
    background: rgba(15, 12, 9, 0);
    transition: background .22s ease;
    pointer-events: none;
}
.kitchen-hotspot-wrap:hover .kitchen-hover-shade {
    background: rgba(15, 12, 9, .18);
}
.kitchen-hotspot {
    position: absolute;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 42px;
    padding: 9px 13px;
    border: 1px solid rgba(238, 214, 169, .95);
    border-radius: 8px;
    background: rgba(31, 25, 19, .91);
    color: #fff2d8 !important;
    font: 600 14px 'Noto Sans KR', sans-serif !important;
    text-decoration: none !important;
    line-height: 1.35;
    text-align: center;
    opacity: 0;
    visibility: hidden;
    transform: translateY(5px);
    transition: opacity .2s ease, transform .2s ease, background .2s ease;
    z-index: 3;
    box-shadow: 0 4px 16px rgba(0,0,0,.22);
}
.kitchen-hotspot-wrap:hover .kitchen-hotspot,
.kitchen-hotspot-wrap:focus-within .kitchen-hotspot {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}
.kitchen-hotspot:hover, .kitchen-hotspot:focus {
    background: rgba(200, 166, 107, .98);
    color: #211910 !important;
    outline: 2px solid #fff2d8;
    outline-offset: 2px;
}
.hotspot-fridge { left: 8%; top: 30%; }
.hotspot-table { left: 39%; top: 68%; }
.hotspot-plant { right: 7%; top: 26%; }
.hotspot-person { right: 18%; bottom: 12%; }

.kitchen-hover-hint {
    margin-top: .7rem;
    color: #c8b9a4;
    font-size: .88rem;
    text-align: center;
}
@media (max-width: 650px) {
    .kitchen-hotspot { min-height: 34px; padding: 6px 8px; font-size: 11px !important; }
    .hotspot-fridge { left: 3%; top: 25%; }
    .hotspot-table { left: 32%; top: 68%; }
    .hotspot-plant { right: 2%; top: 22%; }
    .hotspot-person { right: 8%; bottom: 8%; }
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 음식 예시 데이터
# -----------------------------
FOODS = {
    "닭가슴살 100g": {
        "kcal": 165, "탄수화물(g)": 0, "단백질(g)": 31,
        "지방(g)": 3.6, "나트륨(mg)": 74, "serving": "100g"
    },
    "달걀 1개": {
        "kcal": 72, "탄수화물(g)": 0.4, "단백질(g)": 6.3,
        "지방(g)": 4.8, "나트륨(mg)": 71, "serving": "1개"
    },
    "흰쌀밥 1공기": {
        "kcal": 300, "탄수화물(g)": 66, "단백질(g)": 5.5,
        "지방(g)": 0.6, "나트륨(mg)": 5, "serving": "약 210g"
    },
    "고구마 100g": {
        "kcal": 130, "탄수화물(g)": 31, "단백질(g)": 1.5,
        "지방(g)": 0.2, "나트륨(mg)": 15, "serving": "100g"
    },
    "바나나 1개": {
        "kcal": 105, "탄수화물(g)": 27, "단백질(g)": 1.3,
        "지방(g)": 0.4, "나트륨(mg)": 1, "serving": "중간 크기 1개"
    },
    "사과 1개": {
        "kcal": 95, "탄수화물(g)": 25, "단백질(g)": 0.5,
        "지방(g)": 0.3, "나트륨(mg)": 2, "serving": "중간 크기 1개"
    },
    "두부 100g": {
        "kcal": 76, "탄수화물(g)": 1.9, "단백질(g)": 8,
        "지방(g)": 4.8, "나트륨(mg)": 7, "serving": "100g"
    },
    "연어 100g": {
        "kcal": 208, "탄수화물(g)": 0, "단백질(g)": 20,
        "지방(g)": 13, "나트륨(mg)": 59, "serving": "100g"
    },
    "그릭요거트 100g": {
        "kcal": 97, "탄수화물(g)": 3.9, "단백질(g)": 9,
        "지방(g)": 5, "나트륨(mg)": 36, "serving": "100g"
    },
    "아몬드 10알": {
        "kcal": 70, "탄수화물(g)": 2.6, "단백질(g)": 2.6,
        "지방(g)": 6.1, "나트륨(mg)": 0, "serving": "약 12g"
    },
    "브로콜리 100g": {
        "kcal": 34, "탄수화물(g)": 6.6, "단백질(g)": 2.8,
        "지방(g)": 0.4, "나트륨(mg)": 33, "serving": "100g"
    },
    "우유 200ml": {
        "kcal": 122, "탄수화물(g)": 9.6, "단백질(g)": 6.4,
        "지방(g)": 6.8, "나트륨(mg)": 86, "serving": "200ml"
    },
    "김치 50g": {
        "kcal": 10, "탄수화물(g)": 1.8, "단백질(g)": 0.7,
        "지방(g)": 0.2, "나트륨(mg)": 250, "serving": "50g"
    },
    "샐러드 1그릇": {
        "kcal": 80, "탄수화물(g)": 12, "단백질(g)": 3,
        "지방(g)": 3, "나트륨(mg)": 120, "serving": "채소 약 150g"
    },
}

# -----------------------------
# 식단 예시 데이터
# -----------------------------
RECIPES = {
    "연어 곡물 볼": [
        "연어 100g", "흰쌀밥 1공기", "브로콜리 100g"
    ],
    "닭가슴살 샐러드": [
        "닭가슴살 100g", "샐러드 1그릇", "달걀 1개"
    ],
    "두부 채소 덮밥": [
        "두부 100g", "흰쌀밥 1공기", "브로콜리 100g"
    ],
    "고구마와 그릭요거트": [
        "고구마 100g", "그릭요거트 100g", "아몬드 10알"
    ],
    "간단한 아침 식사": [
        "달걀 1개", "바나나 1개", "우유 200ml"
    ],
    "균형 잡힌 한식 한 끼": [
        "흰쌀밥 1공기", "닭가슴살 100g",
        "브로콜리 100g", "김치 50g"
    ],
    "연어 샐러드 플레이트": [
        "연어 100g", "샐러드 1그릇", "고구마 100g"
    ],
    "두부 단백질 플레이트": [
        "두부 100g", "달걀 1개", "샐러드 1그릇"
    ],
}

NUTRIENTS = [
    "kcal", "탄수화물(g)", "단백질(g)", "지방(g)", "나트륨(mg)"
]

LABELS = [
    "열량 (kcal)", "탄수화물 (g)", "단백질 (g)",
    "지방 (g)", "나트륨 (mg)"
]


def total_foods(names):
    result = {key: 0 for key in NUTRIENTS}

    for name in names:
        for key in NUTRIENTS:
            result[key] += FOODS[name][key]

    return result


# -----------------------------
# 사이드바 메뉴
# 모든 페이지에서 표시
# -----------------------------
with st.sidebar:
    st.markdown("## THE DINING TABLE")
    st.caption("FOOD · NUTRITION · SUSTAINABILITY")
    st.divider()

    st.markdown("### Explore")

    st.button(
        "🏠 홈으로",
        use_container_width=True,
        on_click=set_page,
        args=("home",),
        key="nav_home"
    )

    st.button(
        "🥗 영양 성분 분석",
        use_container_width=True,
        on_click=set_page,
        args=("nutrition",),
        key="nav_nutrition"
    )

    st.button(
        "🍱 맞춤형 식단",
        use_container_width=True,
        on_click=set_page,
        args=("meal",),
        key="nav_meal"
    )

    st.button(
        "🌱 스마트팜 검색",
        use_container_width=True,
        on_click=set_page,
        args=("farm",),
        key="nav_farm"
    )

    st.button(
        "📊 BMI 안내",
        use_container_width=True,
        on_click=set_page,
        args=("bmi",),
        key="nav_bmi"
    )

    st.divider()
    st.caption("원하는 기능을 클릭하면 해당 화면으로 이동합니다.")


# -----------------------------
# 공통 헤더
# -----------------------------
st.markdown(
    '<div class="brand">THE DINING TABLE</div>'
    '<div class="kicker">FOOD · NUTRITION · A BETTER YOU</div><hr>',
    unsafe_allow_html=True
)


# -----------------------------
# 홈 화면
# -----------------------------
if st.session_state.page == "home":
    if IMAGE_PATH.exists():
        import base64
        image_bytes = IMAGE_PATH.read_bytes()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        suffix = IMAGE_PATH.suffix.lower()
        mime = "image/png" if suffix == ".png" else "image/jpeg"
        st.markdown(
            f"""
            <div class="kitchen-hotspot-wrap">
                <img src="data:{mime};base64,{image_b64}" alt="주방 메인 화면">
                <div class="kitchen-hover-shade"></div>
                <a class="kitchen-hotspot hotspot-fridge" href="?page=nutrition" aria-label="영양 성분 분석">
                    🥗 영양 성분 분석
                </a>
                <a class="kitchen-hotspot hotspot-table" href="?page=meal" aria-label="맞춤형 식단">
                    🍱 맞춤형 식단
                </a>
                <a class="kitchen-hotspot hotspot-plant" href="?page=farm" aria-label="스마트팜 검색">
                    🌱 스마트팜 검색
                </a>
                <a class="kitchen-hotspot hotspot-person" href="?page=bmi" aria-label="BMI 안내">
                    📊 BMI 안내
                </a>
            </div>
            <div class="kitchen-hover-hint">주방 이미지에 마우스를 올리면 기능 메뉴가 나타납니다. 메뉴를 클릭해 이동하세요.</div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning("kitchen_home.png를 main.py와 같은 폴더에 업로드해주세요.")

    st.markdown('<div class="kicker">A THOUGHTFUL WAY TO EAT</div>', unsafe_allow_html=True)
    st.markdown("## Discover your table.")
    st.write("식품 영양 정보부터 맞춤형 식단, 지속 가능한 먹거리까지 한곳에서 확인하세요.")
    st.info("주방 이미지 위에 마우스를 올려 원하는 기능을 선택하거나, 왼쪽 메뉴를 이용하세요.")


# -----------------------------
# 영양 성분 분석
# -----------------------------
elif st.session_state.page == "nutrition":

    if st.button("← 홈으로 돌아가기", key="nutrition_back"):
        back_home()

    st.header("Nutrition Check")
    st.write("식품을 선택해 영양 성분을 확인하고 섭취 기록을 관리하세요.")

    food = st.selectbox("식품 선택", list(FOODS.keys()))
    qty = st.number_input(
        "섭취 단위 수",
        min_value=0.25,
        max_value=20.0,
        value=1.0,
        step=0.25
    )

    info = FOODS[food]
    cols = st.columns(5)

    for col, key, label in zip(cols, NUTRIENTS, LABELS):
        col.metric(label, f"{info[key] * qty:.1f}")

    st.caption(
        f"기준 제공량: {info['serving']} · 선택 수량: {qty:g}"
    )

    if st.button("오늘 섭취 기록에 추가"):
        st.session_state.intake.append({
            "식품": food,
            "수량": qty,
            **{key: info[key] * qty for key in NUTRIENTS}
        })
        st.success("오늘 섭취 기록에 추가했습니다.")

    if st.session_state.intake:
        st.subheader("오늘의 섭취 기록")

        df = pd.DataFrame(st.session_state.intake)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        cols = st.columns(5)

        for col, key, label in zip(cols, NUTRIENTS, LABELS):
            col.metric(
                f"합계 {label}",
                f"{df[key].sum():.1f}"
            )

        if st.button("오늘 기록 초기화"):
            st.session_state.intake = []
            st.rerun()

    st.caption(
        "내장된 예시 데이터입니다. 정확한 수치는 제품 표시와 "
        "공식 식품 영양 데이터베이스를 확인하세요."
    )


# -----------------------------
# 맞춤형 식단
# -----------------------------
elif st.session_state.page == "meal":

    if st.button("← 홈으로 돌아가기", key="meal_back"):
        back_home()

    st.header("Meal Planner")
    st.write("메뉴를 선택해 식단 구성과 예상 영양 정보를 확인하세요.")

    recipe = st.selectbox(
        "식단 메뉴 선택",
        list(RECIPES.keys())
    )

    st.subheader(recipe)
    st.write("구성 식품: " + " · ".join(RECIPES[recipe]))

    totals = total_foods(RECIPES[recipe])
    cols = st.columns(5)

    for col, key, label in zip(cols, NUTRIENTS, LABELS):
        col.metric(label, f"{totals[key]:.1f}")

    if st.button("다른 메뉴 추천받기"):
        st.session_state.suggestion = random.choice(
            [name for name in RECIPES if name != recipe]
        )

    if st.session_state.suggestion:
        suggested = st.session_state.suggestion

        st.markdown(f"### 추천 메뉴: {suggested}")
        st.write("구성 식품: " + " · ".join(RECIPES[suggested]))

        totals_suggested = total_foods(RECIPES[suggested])
        cols = st.columns(5)

        for col, key, label in zip(cols, NUTRIENTS, LABELS):
            col.metric(label, f"{totals_suggested[key]:.1f}")

    st.caption(
        "식단 영양값은 식품별 예시 데이터를 합산한 추정치입니다."
    )


# -----------------------------
# 스마트팜 및 친환경 먹거리 검색
# -----------------------------
elif st.session_state.page == "farm":

    if st.button("← 홈으로 돌아가기", key="farm_back"):
        back_home()

    st.header("Smart Farm & Sustainable Food")
    st.write("지역과 검색 대상을 선택해 네이버 지도에서 관련 업체를 찾아보세요.")

    region = st.text_input(
        "지역 입력",
        placeholder="예: 청주시 흥덕구"
    )

    category = st.selectbox(
        "검색 대상",
        [
            "스마트팜 기업",
            "스마트팜 체험농장",
            "친환경 채소 판매처",
            "로컬푸드 직매장"
        ]
    )

    if st.button("네이버 지도에서 검색"):
        if not region.strip():
            st.warning("지역을 먼저 입력해주세요.")
        else:
            url = (
                "https://map.naver.com/p/search/"
                + quote_plus(f"{region.strip()} {category}")
            )
            st.link_button(
                "네이버 지도 열기",
                url,
                use_container_width=True
            )

    st.caption(
        "검색 결과의 주소, 영업 여부, 재배 방식은 업체 정보를 통해 "
        "다시 확인하세요."
    )


# -----------------------------
# BMI 안내
# -----------------------------
elif st.session_state.page == "bmi":

    if st.button("← 홈으로 돌아가기", key="bmi_back"):
        back_home()

    st.header("BMI Guide")

    st.write(
        "BMI는 체중 상태를 단독으로 판단하는 기준이 아닙니다. "
        "청소년은 성장 단계와 연령·성별별 기준을 함께 고려해야 합니다."
    )

    weight = st.number_input(
        "체중 (kg)",
        min_value=1.0,
        max_value=300.0,
        value=60.0,
        step=0.5
    )

    height = st.number_input(
        "키 (cm)",
        min_value=50.0,
        max_value=230.0,
        value=165.0,
        step=0.5
    )

    if st.button("BMI 계산"):
        bmi = weight / ((height / 100) ** 2)

        st.metric("계산된 BMI", f"{bmi:.1f}")

        st.info(
            "청소년은 성인 BMI 분류를 그대로 적용하지 말고 "
            "연령·성별 성장도표와 공식 보건 자료를 확인하세요."
        )


# -----------------------------
# 하단
# -----------------------------
st.markdown("---")

st.markdown(
    "<p style='text-align:center;color:#9e8d79;"
    "font-family:Noto Sans KR,sans-serif;letter-spacing:.08em;'>"
    "THE DINING TABLE · FOOD / NUTRITION / SUSTAINABILITY</p>",
    unsafe_allow_html=True
)
