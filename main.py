import streamlit as st
import pandas as pd
from pathlib import Path
from urllib.parse import quote_plus
import random

st.set_page_config(page_title="THE DINING TABLE", page_icon="🍽️", layout="wide")
BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "kitchen_home.png"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Noto+Sans+KR:wght@400;500;600;700&display=swap');
:root { --bg:#171310; --panel:#241d17; --gold:#c8a66b; --line:#59452f; --text:#eee6da; --muted:#b8aa98; }
html, body, [class*="css"] { font-family:'Noto Sans KR',sans-serif; }
.stApp { background:var(--bg); color:var(--text); }
[data-testid="stHeader"] { background:rgba(23,19,16,.94); }
.block-container { max-width:1240px; padding-top:1.2rem; }
h1,h2,h3,.brand,.kicker { font-family:'Cormorant Garamond',serif !important; color:#f1e5d3 !important; }
.brand { font-size:clamp(2rem,4vw,3.4rem); letter-spacing:.16em; line-height:1.1; }
.kicker { color:var(--gold) !important; font-size:.95rem; letter-spacing:.22em; }
p,li,label,[data-testid="stWidgetLabel"] { color:var(--text); }
a { color:#e0c28c !important; }
.panel { background:linear-gradient(145deg,#30251c,#1e1915); border:1px solid var(--line); border-radius:5px; padding:1.2rem; }
div.stButton>button { width:100%; min-height:3rem; border:1px solid #715638; border-radius:3px; background:#282019; color:#f0e4d2; transition:all .2s ease; }
div.stButton>button:hover { border-color:var(--gold); background:#3a2b1e; color:#fff2d8; }
[data-testid="stMetric"] { background:#241d17; border:1px solid var(--line); border-radius:5px; padding:.8rem; }
hr { border-color:var(--line) !important; }
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page = "home"
if "intake" not in st.session_state: st.session_state.intake = []
if "suggestion" not in st.session_state: st.session_state.suggestion = ""

FOODS = {
    "닭가슴살 100g": {"kcal":165,"탄수화물(g)":0,"단백질(g)":31,"지방(g)":3.6,"나트륨(mg)":74,"serving":"100g"},
    "달걀 1개": {"kcal":72,"탄수화물(g)":0.4,"단백질(g)":6.3,"지방(g)":4.8,"나트륨(mg)":71,"serving":"1개"},
    "흰쌀밥 1공기": {"kcal":300,"탄수화물(g)":66,"단백질(g)":5.5,"지방(g)":0.6,"나트륨(mg)":5,"serving":"약 210g"},
    "고구마 100g": {"kcal":130,"탄수화물(g)":31,"단백질(g)":1.5,"지방(g)":0.2,"나트륨(mg)":15,"serving":"100g"},
    "바나나 1개": {"kcal":105,"탄수화물(g)":27,"단백질(g)":1.3,"지방(g)":0.4,"나트륨(mg)":1,"serving":"중간 크기 1개"},
    "사과 1개": {"kcal":95,"탄수화물(g)":25,"단백질(g)":0.5,"지방(g)":0.3,"나트륨(mg)":2,"serving":"중간 크기 1개"},
    "두부 100g": {"kcal":76,"탄수화물(g)":1.9,"단백질(g)":8,"지방(g)":4.8,"나트륨(mg)":7,"serving":"100g"},
    "연어 100g": {"kcal":208,"탄수화물(g)":0,"단백질(g)":20,"지방(g)":13,"나트륨(mg)":59,"serving":"100g"},
    "그릭요거트 100g": {"kcal":97,"탄수화물(g)":3.9,"단백질(g)":9,"지방(g)":5,"나트륨(mg)":36,"serving":"100g"},
    "아몬드 10알": {"kcal":70,"탄수화물(g)":2.6,"단백질(g)":2.6,"지방(g)":6.1,"나트륨(mg)":0,"serving":"약 12g"},
    "브로콜리 100g": {"kcal":34,"탄수화물(g)":6.6,"단백질(g)":2.8,"지방(g)":0.4,"나트륨(mg)":33,"serving":"100g"},
    "우유 200ml": {"kcal":122,"탄수화물(g)":9.6,"단백질(g)":6.4,"지방(g)":6.8,"나트륨(mg)":86,"serving":"200ml"},
    "김치 50g": {"kcal":10,"탄수화물(g)":1.8,"단백질(g)":0.7,"지방(g)":0.2,"나트륨(mg)":250,"serving":"50g"},
    "샐러드 1그릇": {"kcal":80,"탄수화물(g)":12,"단백질(g)":3,"지방(g)":3,"나트륨(mg)":120,"serving":"채소 약 150g"},
}
RECIPES = {
    "연어 곡물 볼":["연어 100g","흰쌀밥 1공기","브로콜리 100g"],
    "닭가슴살 샐러드":["닭가슴살 100g","샐러드 1그릇","달걀 1개"],
    "두부 채소 덮밥":["두부 100g","흰쌀밥 1공기","브로콜리 100g"],
    "고구마와 그릭요거트":["고구마 100g","그릭요거트 100g","아몬드 10알"],
    "간단한 아침 식사":["달걀 1개","바나나 1개","우유 200ml"],
    "균형 잡힌 한식 한 끼":["흰쌀밥 1공기","닭가슴살 100g","브로콜리 100g","김치 50g"],
    "연어 샐러드 플레이트":["연어 100g","샐러드 1그릇","고구마 100g"],
    "두부 단백질 플레이트":["두부 100g","달걀 1개","샐러드 1그릇"],
}
NUTRIENTS = ["kcal","탄수화물(g)","단백질(g)","지방(g)","나트륨(mg)"]
LABELS = ["열량 (kcal)","탄수화물 (g)","단백질 (g)","지방 (g)","나트륨 (mg)"]

def total_foods(names):
    result = {k:0 for k in NUTRIENTS}
    for name in names:
        for k in NUTRIENTS: result[k] += FOODS[name][k]
    return result

def set_page(page):
    st.session_state.page = page

st.markdown('<div class="brand">THE DINING TABLE</div><div class="kicker">FOOD · NUTRITION · A BETTER YOU</div><hr>', unsafe_allow_html=True)

if st.session_state.page == "home":
    if IMAGE_PATH.exists():
        st.image(str(IMAGE_PATH), use_container_width=True)
    else:
        st.warning("kitchen_home.png를 main.py와 같은 폴더에 업로드해주세요.")
    st.markdown('<div class="kicker">A THOUGHTFUL WAY TO EAT</div>', unsafe_allow_html=True)
    st.markdown("## Discover your table.")
    st.write("식품 영양 정보부터 맞춤형 식단, 지속 가능한 먹거리까지 한곳에서 확인하세요.")
    left, right = st.columns([1, 1.5], gap="large")
    with left:
        st.markdown('<div class="panel"><div class="kicker">EXPLORE</div><h2>Your daily table</h2><p>메뉴를 선택해 기능을 이용하세요.</p></div>', unsafe_allow_html=True)
        for title, desc, page in [
            ("Nutrition Check","식품 영양 성분 확인","nutrition"),
            ("Meal Planner","맞춤형 식단 추천","meal"),
            ("Smart Farm","친환경 채소 · 스마트팜 찾기","farm"),
            ("BMI Guide","BMI 참고 정보","bmi"),
        ]:
            if st.button(f"{title}  ↗  |  {desc}", key=f"home_{page}"):
                set_page(page); st.rerun()
    with right:
        st.markdown('<div class="panel"><div class="kicker">OUR PHILOSOPHY</div><h2>Good food. Considered living.</h2><p>좋은 식사는 몸을 이해하는 일에서 시작합니다. 먹는 음식의 영양을 확인하고, 일상에 맞는 식단을 계획하며, 지속 가능한 먹거리와 연결됩니다.</p><hr><div class="kicker">NUTRITION · BALANCE · SUSTAINABILITY</div></div>', unsafe_allow_html=True)

elif st.session_state.page == "nutrition":
    if st.button("← Back to Home"): set_page("home"); st.rerun()
    st.header("Nutrition Check")
    food = st.selectbox("식품 선택", list(FOODS.keys()))
    qty = st.number_input("섭취 단위 수", 0.25, 20.0, 1.0, 0.25)
    info = FOODS[food]
    cols = st.columns(5)
    for c,k,l in zip(cols,NUTRIENTS,LABELS): c.metric(l, f"{info[k]*qty:.1f}")
    st.caption(f"기준 제공량: {info['serving']} · 선택 수량: {qty:g}")
    if st.button("오늘 섭취 기록에 추가"):
        st.session_state.intake.append({"식품":food,"수량":qty,**{k:info[k]*qty for k in NUTRIENTS}})
        st.success("오늘 섭취 기록에 추가했습니다.")
    if st.session_state.intake:
        st.subheader("오늘의 섭취 기록")
        df = pd.DataFrame(st.session_state.intake)
        st.dataframe(df, use_container_width=True, hide_index=True)
        cols = st.columns(5)
        for c,k,l in zip(cols,NUTRIENTS,LABELS): c.metric(f"합계 {l}", f"{df[k].sum():.1f}")
        if st.button("오늘 기록 초기화"): st.session_state.intake=[]; st.rerun()
    st.caption("내장된 예시 데이터입니다. 정확한 수치는 제품 표시와 공식 식품 영양 데이터베이스를 확인하세요.")

elif st.session_state.page == "meal":
    if st.button("← Back to Home"): set_page("home"); st.rerun()
    st.header("Meal Planner")
    recipe = st.selectbox("식단 메뉴 선택", list(RECIPES.keys()))
    st.subheader(recipe)
    st.write("구성 식품: " + " · ".join(RECIPES[recipe]))
    totals = total_foods(RECIPES[recipe])
    cols = st.columns(5)
    for c,k,l in zip(cols,NUTRIENTS,LABELS): c.metric(l, f"{totals[k]:.1f}")
    if st.button("다른 메뉴 추천받기"):
        st.session_state.suggestion = random.choice([r for r in RECIPES if r != recipe])
    if st.session_state.suggestion:
        s = st.session_state.suggestion
        st.markdown(f"### 추천 메뉴: {s}")
        st.write("구성 식품: " + " · ".join(RECIPES[s]))
        t = total_foods(RECIPES[s])
        cols = st.columns(5)
        for c,k,l in zip(cols,NUTRIENTS,LABELS): c.metric(l, f"{t[k]:.1f}")
    st.caption("식단 영양값은 식품별 예시 데이터를 합산한 추정치입니다.")

elif st.session_state.page == "farm":
    if st.button("← Back to Home"): set_page("home"); st.rerun()
    st.header("Smart Farm & Sustainable Food")
    st.write("지역을 입력하면 네이버 지도에서 관련 업체를 검색합니다.")
    region = st.text_input("지역 입력", placeholder="예: 청주시 흥덕구")
    category = st.selectbox("검색 대상", ["스마트팜 기업","스마트팜 체험농장","친환경 채소 판매처","로컬푸드 직매장"])
    if st.button("네이버 지도에서 검색"):
        if not region.strip(): st.warning("지역을 먼저 입력해주세요.")
        else:
            url = "https://map.naver.com/p/search/" + quote_plus(f"{region.strip()} {category}")
            st.link_button("네이버 지도 열기", url, use_container_width=True)
    st.caption("검색 결과의 주소, 영업 여부, 재배 방식은 업체 정보를 통해 다시 확인하세요.")

elif st.session_state.page == "bmi":
    if st.button("← Back to Home"): set_page("home"); st.rerun()
    st.header("BMI Guide")
    st.write("BMI는 체중 상태를 단독으로 판단하는 기준이 아닙니다. 청소년은 성장 단계와 연령·성별별 기준을 함께 고려해야 합니다.")
    weight = st.number_input("체중 (kg)", 1.0, 300.0, 60.0, 0.5)
    height = st.number_input("키 (cm)", 50.0, 230.0, 165.0, 0.5)
    if st.button("BMI 계산"):
        st.metric("계산된 BMI", f"{weight / ((height/100)**2):.1f}")
        st.info("청소년은 성인 BMI 분류를 그대로 적용하지 말고 연령·성별 성장도표와 공식 보건 자료를 확인하세요.")

st.markdown("---")
st.markdown("<p style='text-align:center;color:#9e8d79;font-family:Cormorant Garamond,serif;letter-spacing:.18em;'>THE DINING TABLE · FOOD / NUTRITION / SUSTAINABILITY</p>", unsafe_allow_html=True)
