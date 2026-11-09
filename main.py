# 이미지 파일을 HTML 화면에 표시하고, 정규식·경로·문자열 정리 기능을 사용하기 위한 모듈
import base64
import re
from pathlib import Path
from urllib.parse import quote_plus
import unicodedata
import html

# CSV 데이터를 표 형태로 처리하고, 카카오 API 및 지도 라이브러리와 Streamlit 화면을 구성합니다.
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
import streamlit as st

# --------------------------------------------------
# 기본 설정 및 데이터 불러오기
# --------------------------------------------------
# 브라우저 탭 제목과 화면 배치 등 Streamlit 앱의 기본 표시 방식을 설정합니다.
st.set_page_config(
    page_title="THE DINING TABLE",
    page_icon="T",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 현재 main.py가 저장된 폴더를 기준으로 데이터 폴더와 홈 이미지를 찾습니다.
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
IMAGE_PATH = BASE_DIR / "kitchen_home.png"

# 데이터 파일은 반복 실행 때마다 다시 읽지 않도록 캐시에 저장합니다.
# 세 CSV 파일을 읽고, 영양 계산에 사용할 수 있도록 숫자형 열을 변환하는 함수입니다.
@st.cache_data(show_spinner=False)
def load_data():
    """data 폴더의 음식 목록, 영양성분, 연결표를 불러옵니다."""
    catalog_path = DATA_DIR / "food_catalog.csv"
    nutrition_path = DATA_DIR / "nutrition_data.csv"
    links_path = DATA_DIR / "food_nutrition_links.csv"

    missing = [p.name for p in [catalog_path, nutrition_path, links_path] if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "data 폴더에서 다음 파일을 찾을 수 없습니다: " + ", ".join(missing)
        )

    catalog_cols = [
        "catalog_id", "catalog_type", "food_name", "food_category",
        "representative_name", "nutrition_match_count", "match_status"
    ]
    nutrition_cols = [
        "food_code", "nutrition_food_name", "nutrition_data_type", "nutrient_basis",
        "kcal", "carbohydrate_g", "sugars_g", "fiber_g", "protein_g", "fat_g",
        "saturated_fat_g", "trans_fat_g", "sodium_mg", "calcium_mg", "iron_mg",
        "potassium_mg", "vitamin_a_ug_rae", "vitamin_c_mg", "cholesterol_mg"
    ]
    link_cols = ["catalog_id", "food_code"]

    # 식품 목록·영양 자료·연결표를 각각 읽습니다. ID를 문자열로 유지해 코드 형식이 바뀌지 않게 합니다.
    catalog = pd.read_csv(
        catalog_path, encoding="utf-8-sig", dtype=str, usecols=catalog_cols
    ).fillna("")
    nutrition = pd.read_csv(
        nutrition_path, encoding="utf-8-sig", dtype={"food_code": str},
        usecols=nutrition_cols, low_memory=False
    )
    links = pd.read_csv(
        links_path, encoding="utf-8-sig", dtype=str, usecols=link_cols
    ).fillna("")

    numeric_cols = [
        "kcal", "carbohydrate_g", "sugars_g", "fiber_g", "protein_g",
        "fat_g", "saturated_fat_g", "trans_fat_g", "sodium_mg",
        "calcium_mg", "iron_mg", "potassium_mg", "vitamin_a_ug_rae",
        "vitamin_c_mg", "cholesterol_mg"
    ]
    # 영양값 열은 계산이 가능하도록 숫자로 바꾸고, 변환할 수 없는 값은 결측치로 처리합니다.
    for col in numeric_cols:
        if col in nutrition.columns:
            nutrition[col] = pd.to_numeric(nutrition[col], errors="coerce")

    return catalog, nutrition, links

# 홈 화면을 먼저 빠르게 띄우고, 영양 분석/식단 메뉴에 들어갈 때만 데이터를 읽습니다.
CATALOG, NUTRITION, LINKS = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
DATA_READY = False
DATA_ERROR = ""
DATA_ATTEMPTED = False

# 영양 분석이나 식단 페이지에 처음 들어왔을 때만 데이터를 불러오도록 관리합니다.
def ensure_data_loaded():
    global CATALOG, NUTRITION, LINKS, DATA_READY, DATA_ERROR, DATA_ATTEMPTED
    if DATA_ATTEMPTED:
        return DATA_READY
    DATA_ATTEMPTED = True
    try:
