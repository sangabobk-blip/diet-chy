import streamlit as st
import pandas as pd
from urllib.parse import quote_plus
from pathlib import Path

# Clickable image component: pip install streamlit-image-coordinates
from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(page_title="그린테이블", page_icon="🌿", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    font-family: 'Noto Sans KR', sans-serif;
}
.stApp { background: #f5f7f4; color: #24352d; }
.block-container { max-width: 1180px; padding-top: 1.4rem; }
h1, h2, h3 { color: #245c43; letter-spacing: -0.03em; }
div.stButton > button {
    border: 1px solid #d5e4da; border-radius: 14px; min-height: 3.1rem;
    background: #ffffff; color: #245c43; font-weight: 600;
}
div.stButton > button:hover { border-color: #478767; background: #edf5ef; color: #194d35; }
div[data-testid="stMetric"] {
    background: white; border: 1px solid #e1e9e3; padding: 14px;
    border-radius: 14px;
}
div[data-testid="stAlert"] { border-radius: 12px; }
.gt-sub { color: #66766d; font-size: 0.97rem; }
.gt-card {
    background: white; border: 1px solid #e1e9e3; border-radius: 16px;
    padding: 18px 20px; margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

if "active_area" not in st.session_state:
    st.session_state.active_area = "홈"
if "intake_records" not in st.session_state:
    st.session_state.intake_records = []

FOODS = {
    "흰밥 1공기 (210g)": {"kcal": 273, "carbs": 59, "protein": 5.7, "fat": 0.6, "sodium": 2},
    "현미밥 1공기 (210g)": {"kcal": 233, "carbs": 48.3, "protein": 5.5, "fat": 1.9, "sodium": 2},
    "닭가슴살 100g": {"kcal": 165, "carbs": 0, "protein": 31, "fat": 3.6, "sodium": 74},
    "계란 1개": {"kcal": 72, "carbs": 0.4, "protein": 6.3, "fat": 4.8, "sodium": 71},
    "두부 100g": {"kcal": 76, "carbs": 1.9, "protein": 8, "fat": 4.8, "sodium": 7},
    "브로콜리 100g": {"kcal": 34, "carbs": 7, "protein": 2.8, "fat": 0.4, "sodium": 33},
    "사과 1개 (200g)": {"kcal": 104, "carbs": 28, "protein": 0.5, "fat": 0.3, "sodium": 2},
    "바나나 1개 (100g)": {"kcal": 89, "carbs": 23, "protein": 1.1, "fat": 0.3, "sodium": 1},
    "김치 100g": {"kcal": 18, "carbs": 3.5, "protein": 1.1, "fat": 0.3, "sodium": 550},
    "우유 200ml": {"kcal": 122, "carbs": 9.4, "protein": 6.4, "fat": 6.6, "sodium": 86},
    "요거트 100g": {"kcal": 61, "carbs": 4.7, "protein": 3.5, "fat": 3.3, "sodium": 46},
    "고구마 100g": {"kcal": 86, "carbs": 20, "protein": 1.6, "fat": 0.1, "sodium": 55},
}

RECIPES = {
    "브로콜리 수프와 통밀빵": {"kcal": 320, "protein": 11, "description": "브로콜리·우유·양파를 부드럽게 끓인 수프와 통밀빵", "ingredients": "브로콜리, 우유, 양파, 통밀빵"},
    "닭가슴살 채소 비빔밥": {"kcal": 480, "protein": 32, "description": "현미밥에 닭가슴살과 여러 색 채소를 곁들인 한 그릇 식사", "ingredients": "현미밥, 닭가슴살, 당근, 시금치, 상추, 고추장"},
    "두부 스테이크와 구운 채소": {"kcal": 390, "protein": 21, "description": "노릇하게 구운 두부 스테이크와 제철 채소", "ingredients": "두부, 브로콜리, 파프리카, 버섯, 올리브유"},
    "연어 덮밥": {"kcal": 510, "protein": 29, "description": "구운 연어와 채소를 밥 위에 올린 덮밥", "ingredients": "연어, 밥, 오이, 아보카도, 김"},
    "계란 채소 샌드위치": {"kcal": 340, "protein": 16, "description": "삶은 달걀과 신선한 채소를 넣은 간편 샌드위치", "ingredients": "통밀빵, 달걀, 상추, 토마토, 요거트 소스"},
    "고구마와 요거트 볼": {"kcal": 250, "protein": 9, "description": "찐 고구마와 플레인 요거트, 제철 과일을 곁들인 간식", "ingredients": "고구마, 플레인 요거트, 딸기 또는 바나나"},
    "버섯 두부 덮밥": {"kcal": 420, "protein": 18, "description": "버섯과 두부를 볶아 밥 위에 올린 균형 잡힌 한 끼", "ingredients": "밥, 두부, 버섯, 양파, 간장"},
    "토마토 달걀 볶음과 밥": {"kcal": 400, "protein": 17, "description": "토마토와 달걀을 가볍게 볶아 밥과 함께 먹는 메뉴", "ingredients": "토마토, 달걀, 밥, 쪽파"},
}

SMARTFARM_LINKS = [
    ("스마트팜코리아", "스마트팜 정책·기술·교육 관련 정보를 찾아볼 수 있는 공식 플랫폼", "https://www.smartfarmkorea.net/"),
    ("농림수산식품교육문화정보원", "농업 정보화와 농업 교육 관련 사업·자료 확인", "https://www.epis.or.kr/"),
    ("탄탄대로", "청년농 및 농업 창업 관련 정보 탐색", "https://www.farmmap.kr/"),
    ("농촌진흥청", "작물 재배기술, 농업 연구자료, 친환경 재배 정보", "https://www.rda.go.kr/"),
]

def go_home():
    st.session_state.active_area = "홈"

def show_back_button():
    if st.button("← 주방으로 돌아가기", key=f"back_{st.session_state.active_area}"):
        go_home()
        st.rerun()

def show_clickable_home():
    image_path = Path(__file__).with_name("kitchen_home.png")
    if not image_path.exists():
        st.error("kitchen_home.png 파일을 찾지 못했습니다. main.py와 같은 GitHub 폴더에 업로드해 주세요.")
        return

    st.markdown("### 주방 속 물건을 직접 클릭해 보세요")
    st.caption("물체가 있는 위치를 클릭하면 해당 기능이 열립니다. 클릭 위치가 맞지 않으면 아래 기능 버튼도 이용할 수 있습니다.")

    # The returned x/y coordinates refer to the displayed image.
    clicked = streamlit_image_coordinates(
        str(image_path),
        key="greentable_kitchen_click",
        width=1100,
    )

    if clicked:
        x = clicked.get("x")
        y = clicked.get("y")
        if x is not None and y is not None:
            # Hotspots are percentages of the displayed image dimensions.
            # These defaults are intended for a wide kitchen image and may need adjustment.
            image_width = 1100
            image_height = None
            try:
                from PIL import Image
                with Image.open(image_path) as im:
                    image_height = int(im.height * image_width / im.width)
            except Exception:
                image_height = 400

            xp = x / image_width
            yp = y / image_height

            # Approximate regions: refrigerator left, lunch/meal counter center,
            # plants on the right, and person character at far right.
            if xp <= 0.30 and 0.10 <= yp <= 0.95:
                st.session_state.active_area = "냉장고"
                st.rerun()
            elif 0.30 < xp <= 0.67 and 0.48 <= yp <= 0.95:
                st.session_state.active_area = "도시락"
                st.rerun()
            elif 0.58 < xp <= 0.84 and 0.08 <= yp <= 0.62:
                st.session_state.active_area = "식물"
                st.rerun()
            elif xp > 0.80 and yp >= 0.25:
                st.session_state.active_area = "건강"
                st.rerun()
            else:
                st.info("기능 연결 영역 밖을 클릭했어요. 냉장고, 조리대의 도시락, 식물, 사람 캐릭터 근처를 클릭해 주세요.")

    # Accessible fallback buttons; these are not required for image interaction.
    with st.expander("클릭이 잘 되지 않나요? 기능을 직접 선택할 수 있어요"):
        c1, c2, c3, c4 = st.columns(4)
        options = [
            (c1, "🧊 냉장고", "냉장고"),
            (c2, "🍱 도시락", "도시락"),
            (c3, "🌱 식물", "식물"),
            (c4, "🧑 건강 정보", "건강"),
        ]
        for col, label, area in options:
            if col.button(label, use_container_width=True, key=f"fallback_{area}"):
                st.session_state.active_area = area
                st.rerun()

st.markdown("# 🌿 그린테이블")
st.markdown('<p class="gt-sub">건강한 식습관이 더 나은 내일을 만듭니다.</p>', unsafe_allow_html=True)

if st.session_state.active_area == "홈":
    show_clickable_home()
    st.markdown("---")
    st.markdown("#### 그린테이블에서 할 수 있는 일")
    a, b, c, d = st.columns(4)
    a.markdown("**영양 확인**\n\n음식별 열량과 주요 영양소")
    b.markdown("**식단 추천**\n\n요리 이름과 한 끼 구성")
    c.markdown("**지속가능한 농업**\n\n친환경 채소와 스마트팜 정보")
    d.markdown("**건강 정보**\n\nBMI 계산과 해석 안내")

elif st.session_state.active_area == "냉장고":
    show_back_button()
    st.header("🧊 냉장고 | 음식 영양소 확인")
    st.write("음식과 먹은 양을 선택하면 대략적인 영양 정보를 계산합니다.")
    food = st.selectbox("음식 선택", list(FOODS.keys()))
    quantity = st.number_input("몇 인분/개를 먹었나요?", min_value=0.25, max_value=20.0, value=1.0, step=0.25)
    if st.button("영양소 계산하기", type="primary"):
        f = FOODS[food]
        st.subheader(f"{food} · {quantity:g}배 기준")
        cols = st.columns(4)
        cols[0].metric("열량", f"{f['kcal']*quantity:.0f} kcal")
        cols[1].metric("탄수화물", f"{f['carbs']*quantity:.1f} g")
        cols[2].metric("단백질", f"{f['protein']*quantity:.1f} g")
        cols[3].metric("지방", f"{f['fat']*quantity:.1f} g")
        st.metric("나트륨", f"{f['sodium']*quantity:.0f} mg")
        st.caption("값은 대표적인 식품의 대략적인 예시입니다. 실제 제품·조리법·중량에 따라 달라질 수 있습니다.")
    st.markdown("#### 빠른 음식 검색")
    query = st.text_input("음식 이름 일부 입력")
    if query:
        matches = [x for x in FOODS if query.strip() in x]
        if matches:
            st.write("검색 결과: " + " · ".join(matches))
        else:
            st.info("예시 데이터에서 찾지 못했습니다. 음식 데이터베이스를 추가하면 검색 범위를 넓힐 수 있습니다.")

elif st.session_state.active_area == "도시락":
    show_back_button()
    st.header("🍱 도시락 | 요리 중심 식단 추천")
    st.write("재료만 나열하지 않고 실제 요리 이름과 간단한 설명을 제공합니다.")
    days = st.selectbox("식단 기간", [1, 3, 5, 7], index=1)
    style = st.selectbox("식단 스타일", ["균형 있게", "한식 중심", "채소를 다양하게", "간편식 중심"])
    if st.button("식단 만들기", type="primary"):
        import random
        recipes = list(RECIPES.items())
        random.shuffle(recipes)
        for day in range(days):
            st.markdown(f"### {day+1}일차")
            daily = [recipes[(day * 3 + i) % len(recipes)] for i in range(3)]
            meal_names = ["아침", "점심", "저녁"]
            cols = st.columns(3)
            for col, meal_name, (name, data) in zip(cols, meal_names, daily):
                with col:
                    st.markdown('<div class="gt-card">', unsafe_allow_html=True)
                    st.markdown(f"**{meal_name} · {name}**")
                    st.write(data["description"])
                    st.caption(f"주요 재료: {data['ingredients']}")
                    st.metric("예상 열량", f"{data['kcal']} kcal")
                    st.caption(f"단백질 약 {data['protein']} g · 1인분 예시")
                    st.markdown("</div>", unsafe_allow_html=True)
            st.divider()
    st.caption("식단은 예시이며 개인의 성장 단계, 활동량, 건강 상태에 따라 필요한 양은 다릅니다. 칼로리를 지나치게 제한하는 용도로 사용하지 마세요.")

elif st.session_state.active_area == "식물":
    show_back_button()
    st.header("🪴 식물 | 친환경 채소와 스마트팜")
    st.write("지역과 관심 분야를 입력해 주변 판매처 및 농업 기업을 찾아보세요.")
    region = st.text_input("지역 또는 시·군·구", placeholder="예: 대전 유성구")
    interest = st.selectbox("관심 분야", ["친환경 채소 판매처", "스마트팜 업체", "수직농장·식물공장", "스마트팜 교육·체험", "청년농·농업 창업"])
    if region.strip():
        q = quote_plus(f"{region} {interest}")
        st.markdown(f"[네이버 지도에서 검색하기](https://map.naver.com/p/search/{q})")
        st.markdown(f"[네이버 검색에서 관련 업체 찾기](https://search.naver.com/search.naver?query={q})")
        st.markdown(f"[구글 검색에서 관련 업체 찾기](https://www.google.com/search?q={q})")
    else:
        st.info("지역을 입력하면 해당 지역을 기준으로 검색할 수 있는 링크가 나타납니다.")
    st.markdown("#### 농업·스마트팜 관련 공식 사이트")
    for name, description, url in SMARTFARM_LINKS:
        st.markdown(f"**[{name}]({url})**  \n{description}")
    st.caption("검색 결과의 영업 여부, 인증 상태, 구매 가능 여부는 각 업체에 직접 확인하세요.")

elif st.session_state.active_area == "건강":
    show_back_button()
    st.header("🧑 나의 건강 정보")
    st.write("키와 몸무게를 입력해 BMI를 계산할 수 있습니다.")
    age = st.number_input("나이", min_value=5, max_value=100, value=17)
    height_cm = st.number_input("키(cm)", min_value=80.0, max_value=230.0, value=165.0, step=0.5)
    weight_kg = st.number_input("몸무게(kg)", min_value=15.0, max_value=250.0, value=60.0, step=0.5)
    if st.button("BMI 계산", type="primary"):
        bmi = weight_kg / ((height_cm / 100) ** 2)
        st.metric("BMI", f"{bmi:.1f}")
        if age < 18:
            st.info("18세 미만은 성인 BMI 기준만으로 체중 상태를 판단하지 않습니다. 나이와 성별에 따른 성장도표 백분위수 등을 함께 고려해야 하므로, 이 값만으로 적정 체중이나 감량 필요성을 판단하지 마세요.")
        else:
            st.info("BMI는 체중(kg) ÷ 키(m)²로 계산하는 참고 지표이며 근육량이나 개인의 건강 상태를 직접 측정하지 않습니다. 필요하면 의료 전문가와 함께 해석하세요.")
    st.markdown("#### 함께 기억할 점")
    st.write("적정 체중은 하나의 숫자로 단정하기 어렵습니다. 균형 잡힌 식사, 충분한 수면, 규칙적인 일상 등 전반적인 건강 습관을 함께 살펴보세요.")

st.markdown("---")
if st.session_state.active_area != "홈":
    if st.button("🏠 홈 화면으로", use_container_width=True, key="home_bottom"):
        go_home()
        st.rerun()
st.caption("그린테이블 · 영양 정보와 식단은 참고용이며, 실제 식품의 영양성분과 건강 판단은 공식 자료 및 전문가의 안내를 확인하세요.")
