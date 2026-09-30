import streamlit as st
import pandas as pd
import re
import os
import random

st.set_page_config(page_title="궁중 식탁", page_icon="🍚", layout="wide")

st.markdown("""
<style>
.stApp {
    background-image:
        linear-gradient(rgba(48, 25, 18, 0.42), rgba(48, 25, 18, 0.42)),
        url("https://images.unsplash.com/photo-1528360983277-13d401cdc186?auto=format&fit=crop&w=2400&q=85");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
.stApp { background: linear-gradient(rgba(248,242,226,.96), rgba(238,227,199,.96)); color:#33281f; }
html, body, [class*="css"], p, label, div, span { font-family:"궁서체","Gungsuh","BatangChe",serif; }
h1,h2,h3,h4 { font-family:"궁서체","Gungsuh","BatangChe",serif !important; color:#4a2419 !important; }
.royal-title { text-align:center; color:#54291d; font-size:42px; font-weight:bold; letter-spacing:4px; }
.royal-subtitle { text-align:center; color:#745744; font-size:17px; }
.royal-line { height:3px; background:#8b241c; margin:15px 0 20px; }
.info-box { background:#f5ead0; border-left:5px solid #8b241c; padding:13px 16px; border-radius:5px; }
.food-card { background:#fffbef; border:1px solid #c8ad7f; border-radius:12px; padding:15px; margin-bottom:10px; }
.stButton > button { background:#6b281d; color:#fffaf0; border-radius:7px; font-family:"궁서체","Gungsuh",serif; }
section[data-testid="stSidebar"] { background:#eee2c4; }
[data-testid="stMetric"] { background:#fffaf0; border:1px solid #cdb88e; padding:10px; border-radius:8px; }
</style>
""", unsafe_allow_html=True)

# 테스트용 데이터. food_data.csv가 있으면 CSV를 우선 사용한다.
FOOD_DB = {
    "흰밥":{"category":"밥류","serving":"100g","unit_g":100,"calories":130,"carbs":28,"sugar":0.1,"protein":2.7,"fat":0.3,"sodium":1,"fiber":0.4},
    "현미밥":{"category":"밥류","serving":"100g","unit_g":100,"calories":111,"carbs":23,"sugar":0.4,"protein":2.6,"fat":0.9,"sodium":1,"fiber":1.8},
    "김밥":{"category":"밥류","serving":"1줄","unit_g":250,"calories":450,"carbs":70,"sugar":5,"protein":12,"fat":12,"sodium":900,"fiber":3},
    "삼각김밥 참치마요":{"category":"편의식","serving":"1개","unit_g":120,"calories":230,"carbs":34,"sugar":2,"protein":6,"fat":8,"sodium":500,"fiber":1},
    "닭가슴살":{"category":"육류","serving":"100g","unit_g":100,"calories":165,"carbs":0,"sugar":0,"protein":31,"fat":3.6,"sodium":74,"fiber":0},
    "계란":{"category":"달걀류","serving":"1개","unit_g":50,"calories":72,"carbs":0.4,"sugar":0.2,"protein":6.3,"fat":4.8,"sodium":71,"fiber":0},
    "두부":{"category":"콩류","serving":"100g","unit_g":100,"calories":76,"carbs":1.9,"sugar":0.5,"protein":8,"fat":4.8,"sodium":7,"fiber":0.3},
    "고등어":{"category":"생선류","serving":"100g","unit_g":100,"calories":205,"carbs":0,"sugar":0,"protein":19,"fat":14,"sodium":90,"fiber":0},
    "연어":{"category":"생선류","serving":"100g","unit_g":100,"calories":208,"carbs":0,"sugar":0,"protein":20,"fat":13,"sodium":59,"fiber":0},
    "김치":{"category":"반찬","serving":"100g","unit_g":100,"calories":18,"carbs":3.5,"sugar":1.5,"protein":1.1,"fat":0.3,"sodium":550,"fiber":2.4},
    "브로콜리":{"category":"채소","serving":"100g","unit_g":100,"calories":34,"carbs":7,"sugar":1.7,"protein":2.8,"fat":0.4,"sodium":33,"fiber":2.6},
    "상추":{"category":"채소","serving":"50g","unit_g":50,"calories":8,"carbs":1.5,"sugar":0.5,"protein":0.7,"fat":0.1,"sodium":8,"fiber":0.7},
    "방울토마토":{"category":"채소","serving":"100g","unit_g":100,"calories":18,"carbs":3.9,"sugar":2.6,"protein":0.9,"fat":0.2,"sodium":5,"fiber":1.2},
    "시금치":{"category":"채소","serving":"100g","unit_g":100,"calories":23,"carbs":3.6,"sugar":0.4,"protein":2.9,"fat":0.4,"sodium":79,"fiber":2.2},
    "바나나":{"category":"과일","serving":"1개","unit_g":100,"calories":89,"carbs":23,"sugar":12,"protein":1.1,"fat":0.3,"sodium":1,"fiber":2.6},
    "사과":{"category":"과일","serving":"1개","unit_g":200,"calories":104,"carbs":28,"sugar":21,"protein":0.5,"fat":0.3,"sodium":2,"fiber":4.8},
    "딸기":{"category":"과일","serving":"100g","unit_g":100,"calories":32,"carbs":7.7,"sugar":4.9,"protein":0.7,"fat":0.3,"sodium":1,"fiber":2},
    "고구마":{"category":"구황작물","serving":"100g","unit_g":100,"calories":86,"carbs":20,"sugar":4.2,"protein":1.6,"fat":0.1,"sodium":55,"fiber":3},
    "감자":{"category":"구황작물","serving":"100g","unit_g":100,"calories":77,"carbs":17,"sugar":0.8,"protein":2,"fat":0.1,"sodium":6,"fiber":2.2},
    "요거트":{"category":"유제품","serving":"100g","unit_g":100,"calories":61,"carbs":4.7,"sugar":4.7,"protein":3.5,"fat":3.3,"sodium":46,"fiber":0},
    "우유":{"category":"유제품","serving":"200ml","unit_g":200,"calories":122,"carbs":9.4,"sugar":9.4,"protein":6.4,"fat":6.6,"sodium":86,"fiber":0},
    "라면":{"category":"면류","serving":"1봉","unit_g":120,"calories":500,"carbs":70,"sugar":3,"protein":10,"fat":20,"sodium":1800,"fiber":2},
    "샌드위치":{"category":"간편식","serving":"1개","unit_g":180,"calories":350,"carbs":40,"sugar":5,"protein":18,"fat":13,"sodium":700,"fiber":3},
    "월남쌈":{"category":"간편식","serving":"1개","unit_g":50,"calories":55,"carbs":8,"sugar":1,"protein":2,"fat":1.5,"sodium":80,"fiber":1},
    "크리스피 도넛":{"category":"디저트","serving":"1개","unit_g":50,"calories":190,"carbs":22,"sugar":10,"protein":2,"fat":11,"sodium":120,"fiber":1},
    "초콜릿 도넛":{"category":"디저트","serving":"1개","unit_g":60,"calories":250,"carbs":30,"sugar":17,"protein":3,"fat":13,"sodium":180,"fiber":1},
    "아이스크림":{"category":"디저트","serving":"100g","unit_g":100,"calories":207,"carbs":24,"sugar":21,"protein":3.5,"fat":11,"sodium":80,"fiber":0},
    "아메리카노":{"category":"음료","serving":"355ml","unit_g":355,"calories":10,"carbs":1,"sugar":0,"protein":0.5,"fat":0,"sodium":5,"fiber":0},
    "카페라떼":{"category":"음료","serving":"355ml","unit_g":355,"calories":180,"carbs":18,"sugar":15,"protein":9,"fat":7,"sodium":120,"fiber":0}
}

def load_food_data():
    if not os.path.exists("food_data.csv"):
        return FOOD_DB
    try:
        df = pd.read_csv("food_data.csv", encoding="utf-8-sig")
        required = ["식품명","중량(g)","칼로리(kcal)","탄수화물(g)","단백질(g)","지방(g)","나트륨(mg)"]
        if not all(c in df.columns for c in required):
            return FOOD_DB
        db = {}
        for _, row in df.iterrows():
            name = str(row["식품명"]).strip()
            if not name:
                continue
            try:
                weight = float(row["중량(g)"])
                db[name] = {
                    "category":str(row.get("식품분류","기타")),
                    "serving":str(row.get("1회 제공량",f"{weight}g")),
                    "unit_g":weight,
                    "calories":float(row["칼로리(kcal)"]),
                    "carbs":float(row["탄수화물(g)"]),
                    "sugar":float(row.get("당류(g)",0)),
                    "protein":float(row["단백질(g)"]),
                    "fat":float(row["지방(g)"]),
                    "sodium":float(row["나트륨(mg)"]),
                    "fiber":float(row.get("식이섬유(g)",0))
                }
            except (ValueError, TypeError):
                continue
        return db if db else FOOD_DB
    except Exception:
        return FOOD_DB

FOOD_DB = load_food_data()

if "intake_list" not in st.session_state:
    st.session_state.intake_list = []

def parse_amount(text, food_name):
    text = text.lower().strip()
    food = FOOD_DB[food_name]

    m = re.search(r"(\d+(?:\.\d+)?)\s*(g|그램)", text)
    if m:
        return float(m.group(1))

    m = re.search(r"(\d+(?:\.\d+)?)\s*(kg|킬로그램)", text)
    if m:
        return float(m.group(1)) * 1000

    if "반공기" in text or "반 공기" in text:
        return 105 if food_name in ["흰밥","현미밥"] else food["unit_g"] * 0.5

    if "한공기" in text or "한 공기" in text:
        return 210 if food_name in ["흰밥","현미밥"] else food["unit_g"]

    m = re.search(r"(\d+(?:\.\d+)?)\s*공기", text)
    if m:
        n = float(m.group(1))
        return n * 210 if food_name in ["흰밥","현미밥"] else n * food["unit_g"]

    if "주먹의 반" in text or "주먹 반" in text or "주먹의 절반" in text:
        return 50
    if "한주먹" in text or "한 주먹" in text or "주먹만큼" in text:
        return 100
    if "한줌" in text or "한 줌" in text:
        return 30
    if "반개" in text or "반 개" in text:
        return food["unit_g"] * 0.5

    m = re.search(r"(\d+(?:\.\d+)?)\s*(개|알|봉|팩|컵|잔|장|줄)", text)
    if m:
        return float(m.group(1)) * food["unit_g"]

    if "한개" in text or "한 개" in text or "하나" in text:
        return food["unit_g"]

    m = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(m.group(1)) if m else None

def find_food(text):
    for name in sorted(FOOD_DB, key=len, reverse=True):
        if name.lower() in text.lower():
            return name
    return None

def nutrition(food_name, amount):
    f = FOOD_DB[food_name]
    r = amount / f["unit_g"]
    return {
        "음식":food_name,
        "섭취량(g)":round(amount,1),
        "칼로리(kcal)":round(f["calories"]*r,1),
        "탄수화물(g)":round(f["carbs"]*r,1),
        "당류(g)":round(f["sugar"]*r,1),
        "단백질(g)":round(f["protein"]*r,1),
        "지방(g)":round(f["fat"]*r,1),
        "나트륨(mg)":round(f["sodium"]*r,1),
        "식이섬유(g)":round(f["fiber"]*r,1)
    }

def parse_multiple(text):
    parts = re.split(r",|\n|그리고|및", text)
    results, errors = [], []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        name = find_food(part)
        if not name:
            errors.append(part)
            continue
        amount = parse_amount(part, name)
        if amount is None:
            errors.append(part)
            continue
        result = nutrition(name, amount)
        result["입력 내용"] = part
        results.append(result)
    return results, errors

def total_nutrition():
    if not st.session_state.intake_list:
        return {k:0 for k in ["칼로리(kcal)","탄수화물(g)","당류(g)","단백질(g)","지방(g)","나트륨(mg)","식이섬유(g)"]}
    df = pd.DataFrame(st.session_state.intake_list)
    return {k:round(df[k].sum(),1) for k in ["칼로리(kcal)","탄수화물(g)","당류(g)","단백질(g)","지방(g)","나트륨(mg)","식이섬유(g)"]}

GROUPS = {
    "주식":["흰밥","현미밥","김밥"],
    "단백질":["닭가슴살","계란","두부","고등어","연어"],
    "채소":["브로콜리","상추","방울토마토","시금치"],
    "과일":["바나나","사과","딸기"],
    "유제품":["우유","요거트"],
    "간식":["고구마","아이스크림","크리스피 도넛","초콜릿 도넛"]
}

def make_meal(meal_type, style):
    if style == "가볍게":
        main = random.choice(["현미밥","고구마"])
    else:
        main = random.choice(GROUPS["주식"])
    meal = [main, random.choice(GROUPS["단백질"])]
    meal += random.sample(GROUPS["채소"], 2)
    meal.append("김치")
    if meal_type == "아침":
        meal.append(random.choice(GROUPS["유제품"] + GROUPS["과일"]))
    else:
        meal.append(random.choice(GROUPS["과일"]))
    return meal

st.markdown('<div class="royal-title">🍚 궁중 식탁</div><div class="royal-subtitle">식품 영양 성분 분석 · 섭취 기록 · 맞춤 식단 관리</div><div class="royal-line"></div>', unsafe_allow_html=True)
st.markdown('<div class="info-box">오늘 먹은 음식을 기록하고 식품의 영양성분을 확인해보세요.</div>', unsafe_allow_html=True)

st.sidebar.title("👤 나의 정보")
age = st.sidebar.number_input("나이", 10, 100, 17)
height = st.sidebar.number_input("키(cm)", 100.0, 220.0, 165.0)
weight = st.sidebar.number_input("몸무게(kg)", 25.0, 150.0, 60.0)
activity = st.sidebar.selectbox("평소 활동량", ["낮음","보통","높음"])
st.sidebar.divider()
st.sidebar.caption(f"현재 식품 데이터: {len(FOOD_DB)}개")
if os.path.exists("food_data.csv"):
    st.sidebar.success("food_data.csv 연결됨")
else:
    st.sidebar.info("현재 테스트용 데이터를 사용합니다.")

tab1, tab2, tab3, tab4 = st.tabs(["🔎 음식 검색","🍽️ 섭취 기록","📊 영양 분석","🥢 식단 만들기"])

with tab1:
    st.header("🔎 음식 검색")
    search = st.text_input("음식 이름을 검색하세요.", placeholder="예: 크리스피 도넛 / 닭가슴살 / 계란")
    if search:
        results = [n for n in FOOD_DB if search.lower() in n.lower()]
        if results:
            st.success(f"{len(results)}개의 음식을 찾았습니다.")
            for name in results:
                f = FOOD_DB[name]
                st.markdown(f'<div class="food-card"><h3>🍽️ {name}</h3><p>분류: {f["category"]}<br>기준 제공량: {f["serving"]}</p></div>', unsafe_allow_html=True)
                a,b,c,d = st.columns(4)
                a.metric("칼로리",f"{f['calories']} kcal")
                b.metric("탄수화물",f"{f['carbs']} g")
                c.metric("단백질",f"{f['protein']} g")
                d.metric("지방",f"{f['fat']} g")
                e,fcol,g = st.columns(3)
                e.metric("당류",f"{f['sugar']} g")
                fcol.metric("나트륨",f"{f['sodium']} mg")
                g.metric("식이섬유",f"{f['fiber']} g")
        else:
            st.warning("해당 음식이 현재 데이터에 없습니다.")
    else:
        st.write("음식 이름의 일부만 입력해도 검색할 수 있습니다.")

with tab2:
    st.header("🍽️ 오늘 먹은 음식 기록")
    st.markdown('<div class="info-box"><b>입력 예시</b><br>닭가슴살 150g, 계란 2개, 밥 1공기, 김치 한 줌</div>', unsafe_allow_html=True)
    text = st.text_area("섭취한 음식", placeholder="예: 닭가슴살 150g, 계란 2개, 밥 1공기, 김치 한 줌", height=100)
    if st.button("🍽️ 섭취량 분석하기", use_container_width=True):
        if not text.strip():
            st.warning("먹은 음식을 입력해주세요.")
        else:
            results, errors = parse_multiple(text)
            if results:
                st.subheader("🔎 입력 분석 결과")
                for r in results:
                    st.write(f"**{r['입력 내용']}** → {r['음식']} {r['섭취량(g)']}g")
                    saved = r.copy()
                    saved.pop("입력 내용", None)
                    st.session_state.intake_list.append(saved)
                st.success(f"{len(results)}개의 음식이 기록되었습니다.")
            if errors:
                st.warning("인식하지 못한 입력: " + ", ".join(errors))
    st.divider()
    if st.session_state.intake_list:
        df = pd.DataFrame(st.session_state.intake_list)
        cols = ["음식","섭취량(g)","칼로리(kcal)","탄수화물(g)","당류(g)","단백질(g)","지방(g)","나트륨(mg)","식이섬유(g)"]
        st.dataframe(df[cols], use_container_width=True, hide_index=True)
        if st.button("🗑️ 오늘의 기록 전체 삭제"):
            st.session_state.intake_list = []
            st.rerun()
    else:
        st.info("아직 오늘의 섭취 기록이 없습니다.")

with tab3:
    st.header("📊 오늘의 영양 분석")
    t = total_nutrition()
    cols = st.columns(3)
    cols[0].metric("칼로리",f"{t['칼로리(kcal)']} kcal")
    cols[1].metric("탄수화물",f"{t['탄수화물(g)']} g")
    cols[2].metric("단백질",f"{t['단백질(g)']} g")
    cols = st.columns(3)
    cols[0].metric("지방",f"{t['지방(g)']} g")
    cols[1].metric("당류",f"{t['당류(g)']} g")
    cols[2].metric("식이섬유",f"{t['식이섬유(g)']} g")
    chart = pd.DataFrame({"영양소":["탄수화물","단백질","지방","당류","식이섬유"],"섭취량(g)":[t["탄수화물(g)"],t["단백질(g)"],t["지방(g)"],t["당류(g)"],t["식이섬유(g)"]]})
    st.bar_chart(chart.set_index("영양소"))
    st.write(f"현재 기록된 나트륨: **{t['나트륨(mg)']} mg**")
    st.progress(min(t["나트륨(mg)"]/2000,1.0))
    st.caption("영양 기준은 일반적인 비교를 위한 참고값입니다.")

with tab4:
    st.header("🥢 맞춤 식단 만들기")
    days = st.slider("식단 기간",1,7,3)
    style = st.selectbox("식단 스타일",["균형 있게","가볍게","한식 중심","좋아하는 음식을 포함"])
    meals = st.multiselect("식단을 만들 식사",["아침","점심","저녁","간식"],default=["아침","점심","저녁"])
    if st.button("🥢 식단 생성하기", use_container_width=True):
        if not meals:
            st.warning("최소 한 가지 식사를 선택해주세요.")
        else:
            for day in range(1,days+1):
                st.subheader(f"📜 {day}일차")
                for meal_type in meals:
                    if meal_type == "간식":
                        st.markdown("**🍵 간식**")
                        st.write(random.choice(GROUPS["간식"]))
                        continue
                    meal = make_meal(meal_type,style)
                    st.markdown(f"**🍚 {meal_type}**")
                    st.write(" · ".join(meal))
                    kcal = sum(FOOD_DB[x]["calories"] for x in meal if x in FOOD_DB)
                    protein = sum(FOOD_DB[x]["protein"] for x in meal if x in FOOD_DB)
                    st.caption(f"구성 예시 기준 약 {kcal:.0f} kcal · 단백질 {protein:.1f}g")
                st.divider()

st.markdown('<div style="text-align:center;color:#755b48;padding:20px;">🍚 궁중 식탁 · Food Nutrition Analysis<br>식품 영양정보 확인 및 식단 계획을 위한 참고용 프로그램</div>', unsafe_allow_html=True)
