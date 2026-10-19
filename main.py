import streamlit as st
import pandas as pd
import re
import os
import random

st.set_page_config(page_title="궁중 식탁", page_icon="🍚", layout="wide")

st.markdown("""
<style>
.stApp { background:#f6f8f7; color:#24332d; }
html, body, [class*="css"], p, label, div, span, input, textarea, button {
    font-family:"Malgun Gothic","Apple SD Gothic Neo",sans-serif;
}
h1,h2,h3,h4 { font-family:"Malgun Gothic","Apple SD Gothic Neo",sans-serif !important; color:#203b31 !important; letter-spacing:-0.5px; }
.main .block-container { padding-top:2rem; padding-bottom:2rem; }
.app-title { text-align:center; color:#203b31; font-size:36px; font-weight:750; letter-spacing:-1px; }
.app-subtitle { text-align:center; color:#687a71; font-size:15px; margin-top:8px; }
.app-line { height:1px; background:#dce5df; margin:20px 0 24px; }
.info-box { background:#edf4ef; border:1px solid #d8e7dc; padding:14px 16px; border-radius:10px; color:#29483a; }
.food-card,.meal-card,.farm-card { background:#fff; border:1px solid #e1e8e3; border-radius:12px; padding:16px 18px; margin-bottom:12px; }
.meal-card h4,.farm-card h4 { margin:0 0 8px 0; }
.stButton > button { background:#2f6650; color:white; border:0; border-radius:8px; padding:.55rem 1rem; font-weight:600; }
.stButton > button:hover { background:#244f3d; color:white; border:0; }
section[data-testid="stSidebar"] { background:#eef3ef; }
[data-testid="stMetric"] { background:#fff; border:1px solid #e1e8e3; padding:12px; border-radius:10px; }
a { color:#2f6650 !important; }
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
