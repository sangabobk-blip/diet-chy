import base64
import re
from pathlib import Path
from urllib.parse import quote_plus
import unicodedata

import pandas as pd
import streamlit as st

# --------------------------------------------------
# 기본 설정 및 데이터 불러오기
# --------------------------------------------------
st.set_page_config(
    page_title="THE DINING TABLE",
    page_icon="T",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
IMAGE_PATH = BASE_DIR / "kitchen_home.png"

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
    for col in numeric_cols:
        if col in nutrition.columns:
            nutrition[col] = pd.to_numeric(nutrition[col], errors="coerce")

    return catalog, nutrition, links

# 홈 화면을 먼저 빠르게 띄우고, 영양 분석/식단 메뉴에 들어갈 때만 데이터를 읽습니다.
CATALOG, NUTRITION, LINKS = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
DATA_READY = False
DATA_ERROR = ""
DATA_ATTEMPTED = False

def ensure_data_loaded():
    global CATALOG, NUTRITION, LINKS, DATA_READY, DATA_ERROR, DATA_ATTEMPTED
    if DATA_ATTEMPTED:
        return DATA_READY
    DATA_ATTEMPTED = True
    try:
        with st.spinner("식품 및 영양성분 데이터를 불러오는 중입니다..."):
            CATALOG, NUTRITION, LINKS = load_data()
        DATA_READY = True
        DATA_ERROR = ""
    except Exception as e:
        DATA_READY = False
        DATA_ERROR = str(e)
    return DATA_READY

VALID_PAGES = {"home", "nutrition", "meal", "profile", "farm", "bmi"}
query_page = st.query_params.get("page")
if query_page in VALID_PAGES:
    st.session_state.page = query_page
elif "page" not in st.session_state or st.session_state.page not in VALID_PAGES:
    st.session_state.page = "home"

if "intake" not in st.session_state:
    st.session_state.intake = []

def set_page(page):
    if page not in VALID_PAGES:
        page = "home"
    st.session_state.page = page
    st.query_params["page"] = page

def back_home():
    set_page("home")

# --------------------------------------------------
# 디자인
# --------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Noto+Sans+KR:wght@400;500;600;700&family=Noto+Serif+KR:wght@400;500;600;700&display=swap');
:root {
    --bg: #171613; --panel: #24211c; --gold: #c8a66b;
    --line: #514637; --text: #eee9df; --muted: #b9b0a2;
    --sage: #8fa58b; --blue: #8da9bd; --rose: #c58f83;
}
html, body, [class*="css"], button, input, textarea, select,
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] {
    font-family: 'Noto Sans KR', sans-serif !important;
}
body, p, li, label, input, textarea, select, button { letter-spacing: -.01em; }
.stApp { background: var(--bg); color: var(--text); }
[data-testid="stHeader"] { background: rgba(23,19,16,.92); }
.block-container { max-width: 1180px; padding-top: 1.2rem; padding-bottom: 2.5rem; }
h1,h2,h3,h4,h5,h6 { color: #f1e8d9 !important; font-family: 'Noto Serif KR', serif !important; font-weight: 600 !important; letter-spacing: -.025em; }
h2 { border-left: 3px solid var(--gold); padding-left: .7rem; }
[data-testid='stMetric'] { background: linear-gradient(145deg, #29251f, #211e19); border: 1px solid #5b4c39; border-radius: 8px; padding: .85rem; }
[data-testid='stMetricValue'] { color: #f2dfbd !important; }
[data-testid='stMetricLabel'] { color: #c5b9a6 !important; }
.brand,.kicker,.english-menu,.sidebar-brand,.sidebar-kicker,.sidebar-section-label,.footer-brand {
    font-family: 'Cormorant Garamond', serif !important;
}
.brand { font-size: clamp(2rem,4vw,3.1rem); letter-spacing: .12em; line-height: 1.1; color: #f1e5d3; }
.kicker { color: var(--gold); font-size: .85rem; letter-spacing: .2em; margin-top: .45rem; }
p,li,label,[data-testid="stWidgetLabel"] { color: var(--text); }
a { color: #e0c28c !important; }
[data-testid="stSidebar"] { background: #201914; border-right: 1px solid var(--line); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { font-family: 'Noto Sans KR',sans-serif !important; }
[data-testid="stSidebar"] .sidebar-brand,[data-testid="stSidebar"] .sidebar-kicker,
[data-testid="stSidebar"] .sidebar-section-label,[data-testid="stSidebar"] .english-menu {
    font-family: 'Cormorant Garamond',serif !important;
}
[data-testid="stSidebar"] .sidebar-brand { font-size: 1.55rem; letter-spacing: .06em; color: #f1e5d3; }
[data-testid="stSidebar"] .sidebar-kicker { color: var(--gold); letter-spacing: .1em; font-size: .83rem; }
div.stButton > button,[data-testid="stLinkButton"] a {
    width: 100%; min-height: 2.8rem; border: 1px solid var(--line);
    border-radius: 4px; background: var(--panel); color: #f0e4d2;
    transition: background .18s ease,border-color .18s ease;
}
div.stButton > button:hover,[data-testid="stLinkButton"] a:hover {
    border-color: var(--gold) !important; background: #392b1f !important; color: #fff2d8 !important;
}
[data-testid="stMetric"] { background: linear-gradient(145deg, #29251f, #211e19); border: 1px solid #5b4c39; border-radius: 8px; padding: .85rem; }
[data-testid="stMetricLabel"] { color: #c5b9a6 !important; }
[data-testid="stAlert"] { border-radius: 8px; border-left-width: 3px; }
[data-testid="stExpander"] { border-color: #5b4c39 !important; border-radius: 8px !important; background: #211e19 !important; }
hr { border-color: var(--line) !important; }
footer { visibility: hidden; }
.kitchen-shell { position: relative; width: 100%; overflow: hidden; border: 1px solid var(--line); border-radius: 5px; background: #211a15; }
.kitchen-shell img { display: block; width: 100%; height: auto; }
.kitchen-hotspot {
    position: absolute; display: flex; align-items: center; justify-content: center;
    text-align: center; text-decoration: none !important; color: #fff5e5 !important;
    border: 1px solid transparent; border-radius: 8px; background: rgba(23,19,16,0);
    min-width: 9%; min-height: 12%; padding: .45rem;
}
.kitchen-hotspot span { opacity: 0; font-size: clamp(.7rem,1.1vw,.95rem); font-weight: 600; text-shadow: 0 1px 4px #000; }
.kitchen-hotspot:hover,.kitchen-hotspot:focus-visible { background: rgba(23,19,16,.76); border-color: var(--gold); }
.kitchen-hotspot:hover span,.kitchen-hotspot:focus-visible span { opacity: 1; }
.hotspot-nutrition { left: 5%; top: 28%; width: 20%; height: 45%; }
.hotspot-meal { left: 31%; top: 53%; width: 27%; height: 34%; }
.hotspot-bmi { left: 57%; top: 25%; width: 19%; height: 48%; }
.hotspot-farm { right: 3%; top: 20%; width: 17%; height: 38%; }
.home-hint { color: var(--muted); font-size: .9rem; margin-top: .65rem; }
.footer-brand { text-align: center; color: #9e8d79; letter-spacing: .15em; font-size: .9rem; }

/* 입력창: 다크 월넛 테마 통일 */
div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"],
[data-testid="stNumberInput"] div[data-baseweb="input"],
[data-testid="stTextInput"] div[data-baseweb="input"] {
    background: #241d17 !important;
    border: 1px solid #59452f !important;
    border-radius: 6px !important;
}
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    background: transparent !important;
    color: #eee6da !important;
}
div[data-baseweb="select"] > div {
    background: #241d17 !important;
    border-color: #59452f !important;
    color: #eee6da !important;
}
div[data-baseweb="select"] span, div[data-baseweb="select"] input {
    color: #eee6da !important;
}
[data-baseweb="popover"], [data-baseweb="menu"], ul[role="listbox"] {
    background: #241d17 !important;
    border: 1px solid #59452f !important;
}
li[role="option"] { color: #eee6da !important; }
li[role="option"]:hover { background: #392b1f !important; }
div[data-baseweb="input"]:focus-within,
div[data-baseweb="select"]:focus-within,
div[data-baseweb="textarea"]:focus-within {
    border-color: #c8a66b !important;
    box-shadow: 0 0 0 1px #c8a66b !important;
}
button[data-baseweb="tab"] {
    color: #b9a995 !important;
    background: #241d17 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #f1e5d3 !important;
    border-bottom-color: #c8a66b !important;
}
[data-testid="stExpander"] {
    border: 1px solid #59452f !important;
    border-radius: 6px !important;
    background: rgba(36,29,23,.55) !important;
}

</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 영양 정보 계산 함수
# --------------------------------------------------
NUTRIENTS = {
    "kcal": ("열량 (kcal)", "kcal"),
    "carbohydrate_g": ("탄수화물 (g)", "g"),
    "protein_g": ("단백질 (g)", "g"),
    "fat_g": ("지방 (g)", "g"),
    "sodium_mg": ("나트륨 (mg)", "mg"),
    "sugars_g": ("당류 (g)", "g"),
    "fiber_g": ("식이섬유 (g)", "g"),
    "calcium_mg": ("칼슘 (mg)", "mg"),
    "iron_mg": ("철 (mg)", "mg"),
    "potassium_mg": ("칼륨 (mg)", "mg"),
    "vitamin_c_mg": ("비타민 C (mg)", "mg"),
}

# 식품 표시에서 사용하는 일반 성인 기준치(개인별 권장량이 아님)
# 청소년·임신부·질환자 등은 연령과 상태에 따라 기준이 달라질 수 있습니다.
DAILY_LABEL_VALUES = {
    "kcal": 2000, "carbohydrate_g": 324, "sugars_g": 100, "fiber_g": 25,
    "protein_g": 55, "fat_g": 54, "sodium_mg": 2000,
    "calcium_mg": 700, "iron_mg": 12, "potassium_mg": 3500,
    "vitamin_c_mg": 100,
}


def food_label(catalog_id):
    row = CATALOG.loc[CATALOG["catalog_id"] == catalog_id].iloc[0]
    return str(row["food_name"])

def linked_rows(catalog_id):
    codes = LINKS.loc[LINKS["catalog_id"] == catalog_id, "food_code"].astype(str).unique()
    return NUTRITION[NUTRITION["food_code"].astype(str).isin(codes)].copy()

def basis_unit(basis):
    text = str(basis).lower().replace(" ", "")
    if "ml" in text:
        return "ml"
    return "g"

def nutrient_values(row, amount):
    """기준량(보통 100g 또는 100ml)에 대한 값을 실제 섭취량으로 환산합니다."""
    basis = str(row.get("nutrient_basis", "100g"))
    unit = basis_unit(basis)
    match = __import__("re").search(r"([0-9]+(?:\.[0-9]+)?)", basis)
    base_amount = float(match.group(1)) if match else 100.0
    multiplier = amount / base_amount if base_amount else 1.0
    result = {}
    for key in NUTRIENTS:
        value = row.get(key, 0)
        result[key] = (0.0 if pd.isna(value) else float(value)) * multiplier
    return result, unit, basis

def show_nutrients(values):
    keys = ["kcal", "carbohydrate_g", "protein_g", "fat_g", "sodium_mg"]
    cols = st.columns(5)
    for col, key in zip(cols, keys):
        col.metric(NUTRIENTS[key][0], f"{values.get(key, 0):,.1f}")

    with st.expander("영양성분 기준치와 비교하기", expanded=False):
        rows = []
        for key, reference in DAILY_LABEL_VALUES.items():
            amount = float(values.get(key, 0) or 0)
            label_name = "열량 (식품표시 참고 기준)" if key == "kcal" else NUTRIENTS[key][0]
            rows.append({
                "영양성분": label_name,
                "이번 섭취량": f"{amount:,.1f} {NUTRIENTS[key][1]}",
                "일반 성인 표시 기준치": f"{reference:,} {NUTRIENTS[key][1]}",
                "기준치 대비": f"{amount / reference * 100:.1f}%" if reference else "-",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption("비교 기준은 식품 영양표시에 사용하는 일반 성인 1일 기준치(열량 2,000kcal 포함)입니다. 개인별 권장 섭취량이나 하루 목표가 아니며, 청소년은 연령·성별·성장 상태와 활동량에 따라 필요한 양이 달라집니다. 이 수치를 식사 제한이나 체중 조절 목표로 사용하지 마세요.")

def choose_nutrition_row(catalog_id, widget_key):
    candidates = linked_rows(catalog_id)
    if candidates.empty:
        return None

    candidates = candidates.sort_values(
        ["nutrition_data_type", "nutrient_basis", "food_code"]
    ).copy()

    # 기준량과 단위가 같은 자료끼리만 평균 후보로 묶습니다.
    candidates["_basis_key"] = candidates["nutrient_basis"].astype(str).str.strip().str.lower()
    groups = {
        basis: group.head(3)
        for basis, group in candidates.groupby("_basis_key", sort=True)
        if len(group) >= 2
    }

    options = []
    option_labels = {}
    for basis, group in groups.items():
        option = f"average::{basis}"
        options.append(option)
        option_labels[option] = (
            f"동일 기준량 자료 평균 ({len(group)}개 · {group.iloc[0]['nutrient_basis']})"
        )

    for idx, row in candidates.iterrows():
        option = f"row::{idx}"
        options.append(option)
        option_labels[option] = (
            f"{row['nutrition_data_type']} · {row['nutrient_basis']} · 코드 {row['food_code']}"
        )

    if len(options) == 1:
        selected = options[0]
    else:
        selected = st.selectbox(
            "영양 정보 선택",
            options,
            format_func=lambda option: option_labels[option],
            key=widget_key,
        )

    if selected.startswith("average::"):
        group = groups[selected.split("::", 1)[1]].copy()
        averaged = group.iloc[0].copy()
        numeric_cols = [
            col for col in NUTRIENTS
            if col in group.columns
        ]
        for col in numeric_cols:
            averaged[col] = pd.to_numeric(group[col], errors="coerce").mean()
        averaged["nutrition_food_name"] = f"{group.iloc[0]['nutrition_food_name']} (자료 평균)"
        averaged["nutrition_data_type"] = f"동일 기준량 {len(group)}개 자료 평균"
        averaged["food_code"] = "평균값"
        return averaged

    row_index = int(selected.split("::", 1)[1])
    return candidates.loc[row_index]

def calculate_meal(selected_ids, quantities, widget_prefix="meal"):
    totals = {key: 0.0 for key in NUTRIENTS}
    detail_rows = []
    for catalog_id, amount in zip(selected_ids, quantities):
        row = choose_nutrition_row(catalog_id, f"{widget_prefix}_source_{catalog_id}")
        if row is None:
            continue
        values, unit, basis = nutrient_values(row, amount)
        for key, value in values.items():
            totals[key] += value
        detail_rows.append({
            "식품": food_label(catalog_id),
            f"섭취량 ({unit})": amount,
            "기준량": basis,
            "열량 (kcal)": round(values["kcal"], 1),
            "탄수화물 (g)": round(values["carbohydrate_g"], 1),
            "단백질 (g)": round(values["protein_g"], 1),
            "지방 (g)": round(values["fat_g"], 1),
        })
    return totals, detail_rows


def normalize_food_name(value):
    """검색 비교를 위해 유니코드와 공백을 정리합니다."""
    value = unicodedata.normalize("NFKC", str(value)).casefold()
    return re.sub(r"\s+", "", value)

def search_catalog(search_text, source_df, limit=300, nutrition_only=False, search_type="전체"):
    """음식명 일부 검색 + 검색어별 일치 + 관련도순 정렬."""
    results = source_df.copy()

    if search_type != "전체":
        results = results[results["catalog_type"] == search_type]

    if nutrition_only:
        results = results[
            pd.to_numeric(results["nutrition_match_count"], errors="coerce").fillna(0) > 0
        ]

    query = normalize_food_name(search_text)
    if query:
        names = results["food_name"].fillna("").map(normalize_food_name)
        # 띄어쓰기로 나눈 검색어가 모두 음식 이름에 포함되는지 확인
        raw_tokens = [normalize_food_name(token) for token in str(search_text).split()]
        tokens = [token for token in raw_tokens if token]
        mask = pd.Series(True, index=results.index)
        for token in tokens:
            mask &= names.str.contains(re.escape(token), regex=True, na=False)
        results = results[mask].copy()

        if not results.empty:
            matched_names = results["food_name"].fillna("").map(normalize_food_name)
            results["_rank"] = matched_names.map(
                lambda name: 0 if name == query else (1 if name.startswith(query) else 2)
            )
            results = results.sort_values(
                ["_rank", "food_name"], kind="stable"
            ).drop(columns="_rank")

    return results.head(limit)


def classify_food_role(food_name, food_category=""):
    """음식명과 분류명을 바탕으로 식단 내 역할을 추정합니다."""
    name = normalize_food_name(food_name)
    category = normalize_food_name(food_category)

    if any(k in name for k in ["김치", "나물", "무침", "장아찌", "깍두기", "겉절이"]):
        return "반찬"
    if any(k in name for k in ["밥", "볶음밥", "주먹밥", "죽", "국수", "면", "파스타"]):
        return "밥·면"
    if any(k in name for k in ["국", "탕", "찌개", "전골", "수프"]):
        return "국·찌개"
    if any(k in name for k in ["불고기", "갈비", "스테이크", "돈까스", "제육", "찜닭",
                               "닭볶음", "생선구이", "구이", "볶음", "튀김", "조림"]):
        return "주메뉴"
    if any(k in name for k in ["사과", "바나나", "귤", "포도", "딸기", "배", "오렌지",
                               "요거트", "요구르트", "우유"]):
        return "과일·간식"
    if any(k in category for k in ["반찬", "김치", "나물"]):
        return "반찬"
    if any(k in category for k in ["밥", "면", "주식"]):
        return "밥·면"
    if any(k in category for k in ["국", "탕", "찌개"]):
        return "국·찌개"
    return "주메뉴"


def recommend_meal_combo(frame, seed_text):
    """CSV에 실제 존재하고 영양자료와 연결된 음식 중 역할별 후보를 추천합니다."""
    import random

    if frame.empty:
        return []

    work = frame.copy()
    work["_role"] = work.apply(
        lambda row: classify_food_role(row.get("food_name", ""), row.get("food_category", "")),
        axis=1
    )
    rng = random.Random()
    selected = []

    # 주메뉴 1개, 밥·면 1개, 국·찌개 1개, 반찬 2개를 우선 구성합니다.
    for role, count in [("주메뉴", 1), ("밥·면", 1), ("국·찌개", 1), ("반찬", 2)]:
        candidates = work[work["_role"] == role]
        if candidates.empty:
            continue
        candidates = candidates.drop_duplicates("food_name")
        indexes = list(candidates.index)
        rng.shuffle(indexes)
        for idx in indexes[:count]:
            food_id = candidates.loc[idx, "catalog_id"]
            if food_id not in selected:
                selected.append(food_id)

    # 특정 역할 자료가 부족한 경우 다른 음식으로 구성하되 중복은 피합니다.
    if len(selected) < 3:
        remaining = work[~work["catalog_id"].isin(selected)].drop_duplicates("food_name")
        indexes = list(remaining.index)
        rng.shuffle(indexes)
        for idx in indexes:
            selected.append(remaining.loc[idx, "catalog_id"])
            if len(selected) >= 5:
                break
    return selected


def portion_choices(food_name, unit):
    """가정용 기준의 대략적인 양을 제공합니다. 표시 중량은 음식·조리법·그릇 크기에 따라 달라질 수 있습니다."""
    name = normalize_food_name(food_name)
    if unit == "ml":
        return [
            ("작은 컵 1/2 (약 100ml)", 100.0),
            ("일반 컵 1잔 (약 200ml)", 200.0),
            ("큰 컵 1잔 (약 250ml)", 250.0),
            ("국그릇 1개 (약 300ml)", 300.0),
            ("직접 입력", None),
        ]
    if any(k in name for k in ["밥", "볶음밥", "주먹밥"]):
        return [
            ("밥 1/2공기 (약 100g)", 100.0),
            ("밥 1공기 (약 210g)", 210.0),
            ("밥 1.5공기 (약 315g)", 315.0),
            ("직접 입력", None),
        ]
    if any(k in name for k in ["국", "탕", "찌개", "전골"]):
        return [
            ("건더기 포함 작은 국그릇 (약 200g)", 200.0),
            ("국그릇 1개 (약 300g)", 300.0),
            ("넉넉한 1그릇 (약 400g)", 400.0),
            ("직접 입력", None),
        ]
    if any(k in name for k in ["김치", "나물", "무침", "반찬"]):
        return [
            ("작은 반찬 접시 (약 30g)", 30.0),
            ("반찬 접시 1개 (약 50g)", 50.0),
            ("넉넉한 반찬 접시 (약 80g)", 80.0),
            ("직접 입력", None),
        ]
    if any(k in name for k in ["계란", "달걀", "바나나", "사과", "감자", "고구마"]):
        return [
            ("작은 것 1개 (약 80g)", 80.0),
            ("보통 크기 1개 (약 120g)", 120.0),
            ("큰 것 1개 (약 180g)", 180.0),
            ("직접 입력", None),
        ]
    if any(k in name for k in ["고기", "불고기", "닭", "생선", "스테이크", "돈까스"]):
        return [
            ("작은 반찬 접시 1개 (약 60g)", 60.0),
            ("손바닥 크기 1조각 (약 100g)", 100.0),
            ("손바닥 크기 2조각 (약 180g)", 180.0),
            ("직접 입력", None),
        ]
    return [
        ("밥숟가락으로 3큰술 정도 (약 45g)", 45.0),
        ("작은 반찬 접시 1개 (약 80g)", 80.0),
        ("일반 접시 1/2 정도 (약 120g)", 120.0),
        ("직접 입력", None),
    ]


def quantity_input(food_id, widget_prefix, basis=None):
    """생활 단위 선택을 기본으로 제공하고 필요할 때만 직접 수치를 입력합니다."""
    candidate_rows = linked_rows(food_id)
    selected_basis = basis if basis is not None else (candidate_rows.iloc[0]["nutrient_basis"] if not candidate_rows.empty else "100g")
    unit = basis_unit(selected_basis)
    choices = portion_choices(CATALOG.loc[CATALOG["catalog_id"] == food_id, "food_name"].iloc[0], unit)
    labels = [item[0] for item in choices]
    selected_label = st.selectbox(
        f"{food_label(food_id)} · 섭취량",
        labels,
        key=f"{widget_prefix}_portion_{food_id}"
    )
    amount = dict(choices)[selected_label]
    if amount is None:
        amount = st.number_input(
            f"직접 입력 ({unit})",
            min_value=1.0,
            max_value=5000.0,
            value=100.0,
            step=10.0,
            key=f"{widget_prefix}_custom_{food_id}"
        )
    else:
        st.caption(f"영양 계산에 적용되는 예상 섭취량: {amount:g}{unit}")
    return float(amount)

# --------------------------------------------------
# 사이드바
# --------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-brand">THE DINING TABLE</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-kicker">FOOD · NUTRITION · SUSTAINABILITY</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="sidebar-section-label">Explore</div>', unsafe_allow_html=True)
    nav_items = [
        ("홈으로", "home", "nav_home"),
        ("영양 성분 분석", "nutrition", "nav_nutrition"),
        ("맞춤형 식단", "meal", "nav_meal"),
        ("사용자 영양 설정", "profile", "nav_profile"),
        ("스마트팜 검색", "farm", "nav_farm"),
        ("BMI 안내", "bmi", "nav_bmi"),
    ]
    for label, page, key in nav_items:
        if st.button(label, use_container_width=True, key=key, type="secondary"):
            set_page(page)
            st.rerun()
    st.divider()
    st.caption("메뉴를 선택하면 해당 기능 화면으로 이동합니다.")

st.markdown(
    '<div class="brand">THE DINING TABLE</div>'
    '<div class="kicker">FOOD · NUTRITION · A BETTER YOU</div><hr>',
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 홈
# --------------------------------------------------
if st.session_state.page == "home":
    if IMAGE_PATH.exists():
        image_data = base64.b64encode(IMAGE_PATH.read_bytes()).decode("utf-8")
        suffix = IMAGE_PATH.suffix.lower()
        mime = "image/png" if suffix == ".png" else "image/jpeg"
        st.markdown(
            f"""<div class="kitchen-shell">
              <img src="data:{mime};base64,{image_data}" alt="주방 메인 화면" />
              <a class="kitchen-hotspot hotspot-nutrition" href="?page=nutrition" target="_top"><span>영양 성분 분석</span></a>
              <a class="kitchen-hotspot hotspot-meal" href="?page=meal" target="_top"><span>맞춤형 식단</span></a>
              <a class="kitchen-hotspot hotspot-bmi" href="?page=bmi" target="_top"><span>BMI 안내</span></a>
              <a class="kitchen-hotspot hotspot-farm" href="?page=farm" target="_top"><span>스마트팜 검색</span></a>
            </div>""",
            unsafe_allow_html=True,
        )
        st.markdown('<div class="home-hint">주방 그림 속 기능 영역에 마우스를 올려 기능을 확인하고 클릭하세요.</div>', unsafe_allow_html=True)
    else:
        st.warning("kitchen_home.png 파일이 없습니다. main.py와 같은 폴더에 업로드해 주세요.")
        cols = st.columns(4)
        for col, (label, page, key) in zip(cols, nav_items[1:]):
            with col:
                if st.button(label, key=f"home_{key}", use_container_width=True):
                    set_page(page)
                    st.rerun()
    st.markdown('<div class="kicker">A THOUGHTFUL WAY TO EAT</div>', unsafe_allow_html=True)
    st.markdown("## Discover your table.")
    st.write("식품 영양 정보부터 맞춤형 식단, 지속 가능한 먹거리까지 한곳에서 확인하세요.")
    st.caption("영양 정보는 영양 성분 분석 또는 맞춤형 식단 메뉴에서 불러옵니다.")

# --------------------------------------------------
# 영양 성분 분석: CSV 검색 및 실제 영양값 계산
# --------------------------------------------------
elif st.session_state.page == "nutrition":
    ensure_data_loaded()
    if not DATA_READY:
        st.error("데이터 파일을 불러오지 못했습니다.")
        st.code(DATA_ERROR)
        st.info("main.py와 같은 위치의 data 폴더에 CSV 파일 3개가 있는지 확인해 주세요.")
    if st.button("← 홈으로 돌아가기", key="nutrition_back"):
        back_home()
        st.rerun()
    st.header("Nutrition Check")
    st.write("음식 이름을 검색하고 실제 영양성분 자료를 확인하세요.")

    if DATA_READY:
        search_type = st.selectbox("음식 종류", ["전체", "일반음식", "가공식품"])
        search_text = st.text_input("음식 검색", placeholder="예: 바나나, 두부, 우유, 과자")
        options_df = search_catalog(
            search_text, CATALOG, limit=300, search_type=search_type
        )
        st.caption(f"검색 결과: {len(options_df):,}개 (최대 300개 표시)")
        if options_df.empty:
            st.warning("검색 결과가 없습니다. 다른 검색어를 입력해 보세요.")
        else:
            ids = options_df["catalog_id"].tolist()
            selected_id = st.selectbox(
                "검색 결과에서 식품 선택",
                ids,
                format_func=food_label,
                key="nutrition_food_select",
            )
            selected_catalog = CATALOG[CATALOG["catalog_id"] == selected_id].iloc[0]
            st.caption(f'분류: {selected_catalog["catalog_type"]} · {selected_catalog["food_category"]}')
            candidate = choose_nutrition_row(selected_id, "nutrition_source_choice")
            if candidate is None:
                st.warning("이 음식은 현재 영양성분 자료와 연결되지 않았습니다. 다른 음식을 검색해 주세요.")
            else:
                amount = quantity_input(selected_id, "nutrition", candidate["nutrient_basis"])
                values, unit, basis = nutrient_values(candidate, amount)
                st.caption(f'영양성분 자료: {candidate["nutrition_food_name"]} · 기준량: {basis} · 자료 구분: {candidate["nutrition_data_type"]}')
                show_nutrients(values)
                with st.expander("영양성분 자세히 보기"):
                    detail_keys = list(NUTRIENTS.keys())
                    detail = []
                    for k in detail_keys:
                        ref = DAILY_LABEL_VALUES.get(k)
                        detail.append({
                            "영양성분": NUTRIENTS[k][0],
                            "섭취량 기준 계산값": round(values[k], 2),
                            "일반 성인 표시 기준치": ref if ref is not None else "별도 기준 없음",
                            "기준치 대비(%)": round(values[k] / ref * 100, 1) if ref else "-",
                        })
                    st.dataframe(pd.DataFrame(detail), use_container_width=True, hide_index=True)
                if st.button("오늘 섭취 기록에 추가", key="add_intake"):
                    st.session_state.intake.append({
                        "식품": selected_catalog["food_name"],
                        "종류": selected_catalog["catalog_type"],
                        f"섭취량({unit})": amount,
                        **{NUTRIENTS[k][0]: round(v, 2) for k, v in values.items()},
                    })
                    st.success("오늘 섭취 기록에 추가했습니다.")

        if st.session_state.intake:
            st.subheader("오늘의 섭취 기록")
            intake_df = pd.DataFrame(st.session_state.intake)
            st.dataframe(intake_df, use_container_width=True, hide_index=True)
            if st.button("오늘 기록 초기화", key="clear_intake"):
                st.session_state.intake = []
                st.rerun()
    st.caption("영양값은 선택한 공식 자료의 기준량을 바탕으로 환산한 값입니다. 실제 제품은 포장지의 표시 정보도 확인하세요.")

# --------------------------------------------------
# 맞춤형 식단: 역할별 추천 + 날짜 탭 + 생활 단위 섭취량
# --------------------------------------------------
elif st.session_state.page == "meal":
    ensure_data_loaded()
    if not DATA_READY:
        st.error("데이터 파일을 불러오지 못했습니다.")
        st.code(DATA_ERROR)
        st.info("main.py와 같은 위치의 data 폴더에 CSV 파일 3개가 있는지 확인해 주세요.")

    if st.button("← 홈으로 돌아가기", key="meal_back"):
        back_home()
        st.rerun()

    st.header("Meal Planner")
    st.write("주메뉴와 반찬을 함께 구성하고, 익숙한 생활 단위로 섭취량을 입력해 보세요.")

    if DATA_READY:
        if "nutrition_profile" not in st.session_state:
            st.session_state.nutrition_profile = {
                "age_group": "청소년",
                "activity": "보통",
                "preferences": [],
                "allergies": [],
                "interests": [],
            }
        profile = st.session_state.nutrition_profile

        meal_days = st.selectbox(
            "식단 계획 기간",
            options=list(range(1, 8)),
            format_func=lambda n: f"{n}일" if n != 7 else "7일 (일주일)",
            key="meal_plan_days",
        )

        st.caption(
            f"현재 설정: {profile['age_group']} · 활동 수준 {profile['activity']} · "
            f"선호 식품 {', '.join(profile['preferences']) if profile['preferences'] else '미설정'}"
        )
        st.info(
            "알레르기 설정은 식품명 기반의 보조 필터입니다. 실제 제품의 원재료와 "
            "교차접촉 정보는 반드시 별도로 확인하세요."
        )

        base_options = search_catalog("", CATALOG, limit=5000, nutrition_only=True).copy()
        allergy_words = [str(x).replace(" ", "").casefold() for x in profile["allergies"]]

        def allergy_filtered(frame):
            if not allergy_words:
                return frame
            names = frame["food_name"].fillna("").map(normalize_food_name)
            blocked = pd.Series(False, index=frame.index)
            for word in allergy_words:
                blocked |= names.str.contains(re.escape(normalize_food_name(word)), na=False)
            return frame[~blocked].copy()

        base_options = allergy_filtered(base_options)

        st.markdown("#### 날짜별 식단 구성")
        st.caption("아래 날짜 탭은 서로 독립적으로 입력할 수 있습니다. 1일차를 완성하지 않아도 다른 날짜를 선택할 수 있습니다.")

        day_tabs = st.tabs([f"{day}일차" for day in range(1, meal_days + 1)])
        all_day_totals = []
        plan_detail_rows = []

        for day_number, day_tab in enumerate(day_tabs, start=1):
            with day_tab:
                st.markdown(f"### {day_number}일차 식단")
                day_totals = {key: 0.0 for key in NUTRIENTS}

                for meal_name in ["아침", "점심", "저녁"]:
                    with st.expander(f"{meal_name} 식단", expanded=(meal_name == "아침")):
                        category_values = sorted(
                            [str(x) for x in base_options["food_category"].dropna().unique()
                             if str(x).strip()]
                        )
                        category = st.selectbox(
                            "식품 카테고리",
                            ["전체 카테고리"] + category_values,
                            key=f"meal_cat_{day_number}_{meal_name}",
                        )
                        search_text = st.text_input(
                            "음식 검색",
                            placeholder="예: 불고기, 잡곡밥, 시금치나물",
                            key=f"meal_search_{day_number}_{meal_name}",
                        )

                        meal_options = search_catalog(
                            search_text, base_options, limit=1500, nutrition_only=False
                        )
                        if category != "전체 카테고리":
                            meal_options = meal_options[
                                meal_options["food_category"].astype(str) == category
                            ]
                        meal_options = meal_options.sort_values("food_name", kind="stable")
                        option_ids = meal_options["catalog_id"].tolist()
                        selection_key = f"meal_selected_{day_number}_{meal_name}"

                        col_recommend, col_reset = st.columns([3, 1])
                        with col_recommend:
                            if st.button(
                                "✦ 주메뉴와 반찬 추천받기",
                                key=f"auto_meal_{day_number}_{meal_name}",
                                use_container_width=True,
                                help="CSV에 등록된 음식 중 주메뉴, 밥·면, 국·찌개, 반찬 후보를 골라 구성합니다.",
                            ):
                                if base_options.empty:
                                    st.warning("추천할 수 있는 영양성분 연결 식품이 없습니다.")
                                else:
                                    recommended = recommend_meal_combo(
                                        base_options,
                                        f"{day_number}-{meal_name}-{profile['preferences']}-{profile['interests']}"
                                    )
                                    st.session_state[selection_key] = recommended
                        with col_reset:
                            if st.button(
                                "선택 초기화",
                                key=f"clear_meal_{day_number}_{meal_name}",
                                use_container_width=True,
                            ):
                                st.session_state[selection_key] = []

                        # 추천 결과가 현재 검색 필터 밖에 있더라도 선택 목록에서 사라지지 않도록 유지합니다.
                        current_selected = st.session_state.get(selection_key, [])
                        display_option_ids = list(dict.fromkeys(option_ids + current_selected))
                        selected_ids = st.multiselect(
                            "식단에 포함할 음식",
                            display_option_ids,
                            format_func=food_label,
                            key=selection_key,
                            help="추천 결과를 수정하거나 검색해서 음식을 추가할 수 있습니다.",
                        )

                        if selected_ids:
                            role_rows = []
                            for food_id in selected_ids:
                                row = CATALOG.loc[CATALOG["catalog_id"] == food_id].iloc[0]
                                role_rows.append({
                                    "음식": row["food_name"],
                                    "식단 역할": classify_food_role(
                                        row["food_name"], row["food_category"]
                                    )
                                })
                            st.dataframe(
                                pd.DataFrame(role_rows),
                                use_container_width=True,
                                hide_index=True,
                            )

                            quantities = []
                            for food_id in selected_ids:
                                quantities.append(
                                    quantity_input(
                                        food_id,
                                        f"meal_{day_number}_{meal_name}"
                                    )
                                )

                            totals, details = calculate_meal(
                                selected_ids,
                                quantities,
                                widget_prefix=f"meal_{day_number}_{meal_name}",
                            )
                            for key, value in totals.items():
                                day_totals[key] += value
                            for detail in details:
                                plan_detail_rows.append({
                                    "날짜": f"{day_number}일차",
                                    "끼니": meal_name,
                                    **detail,
                                })
                            st.dataframe(
                                pd.DataFrame(details),
                                use_container_width=True,
                                hide_index=True,
                            )
                            show_nutrients(totals)
                        else:
                            st.caption("음식을 검색해 선택하거나 '주메뉴와 반찬 추천받기'를 눌러 구성하세요.")

                st.markdown("---")
                st.markdown(f"**{day_number}일차 하루 영양 정보 합계**")
                show_nutrients(day_totals)
                all_day_totals.append((day_number, day_totals))

        st.subheader("기간별 영양 정보 요약")
        summary = []
        for day_number, totals in all_day_totals:
            summary.append({
                "날짜": f"{day_number}일차",
                "열량 (kcal)": round(totals["kcal"], 1),
                "탄수화물 (g)": round(totals["carbohydrate_g"], 1),
                "단백질 (g)": round(totals["protein_g"], 1),
                "지방 (g)": round(totals["fat_g"], 1),
            })
        summary_df = pd.DataFrame(summary)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        st.markdown("#### 식단표 다운로드")
        if plan_detail_rows:
            detail_df = pd.DataFrame(plan_detail_rows)
            st.download_button(
                "식품별 식단표 다운로드 (CSV)",
                data=detail_df.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"식단표_{meal_days}일.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_meal_details",
            )
        else:
            st.info("다운로드하려면 먼저 식단에 음식을 추가해 주세요.")

        st.download_button(
            "기간별 영양 요약 다운로드 (CSV)",
            data=summary_df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"영양요약_{meal_days}일.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_meal_summary",
        )

    st.caption(
        "생활 단위의 g·ml 환산값은 음식과 그릇 크기에 따른 추정치입니다. "
        "정확한 계산이 필요하면 주방저울이나 제품 포장지의 표시량을 이용하세요. "
        "식단은 다양한 식품을 균형 있게 먹기 위한 참고 자료입니다."
    )


# --------------------------------------------------
# 사용자 영양 정보 설정
# --------------------------------------------------
elif st.session_state.page == "profile":
    if st.button("← 홈으로 돌아가기", key="profile_back"):
        back_home()
        st.rerun()

    st.header("My Nutrition Profile")
    st.write("식단 추천에 참고할 기본 정보를 설정하세요.")

    if "nutrition_profile" not in st.session_state:
        st.session_state.nutrition_profile = {
            "age_group": "청소년",
            "activity": "보통",
            "preferences": [],
            "allergies": [],
            "interests": [],
        }

    profile = st.session_state.nutrition_profile

    with st.form("nutrition_profile_form"):
        age_group = st.selectbox(
            "연령대",
            ["청소년", "성인", "중장년", "노년"],
            index=["청소년", "성인", "중장년", "노년"].index(profile["age_group"]),
        )
        activity = st.selectbox(
            "활동 수준",
            ["낮음", "보통", "높음"],
            index=["낮음", "보통", "높음"].index(profile["activity"]),
            help="운동량을 파악하기 위한 참고 정보이며 열량 제한에 사용하지 않습니다.",
        )
        preferences = st.multiselect(
            "음식 선호도",
            ["한식", "채식 위주", "육류 포함", "생선·해산물", "유제품", "간편식"],
            default=profile["preferences"],
        )
        allergies = st.multiselect(
            "알레르기 또는 피하고 싶은 식품",
            ["우유", "달걀", "밀", "땅콩", "대두", "견과류", "생선", "갑각류", "조개류"],
            default=profile["allergies"],
            help="선택한 항목이 식품명에 나타나는 경우 자동 추천 후보에서 제외합니다. 원재료·교차접촉까지 보장하는 알레르기 검사는 아닙니다.",
        )
        interests = st.multiselect(
            "관심 있는 영양 관리 항목",
            ["균형 잡힌 식사", "식이섬유", "단백질", "칼슘", "철분", "비타민", "나트륨 확인", "당류 확인"],
            default=profile["interests"],
        )
        save_profile = st.form_submit_button("설정 저장", use_container_width=True)

    if save_profile:
        st.session_state.nutrition_profile = {
            "age_group": age_group,
            "activity": activity,
            "preferences": preferences,
            "allergies": allergies,
            "interests": interests,
        }
        st.success("사용자 영양 정보 설정을 저장했어요.")

    st.caption(
        "설정은 식품 검색과 자동 구성의 참고 조건으로만 사용됩니다. "
        "알레르기가 있다면 앱의 자동 분류만 믿지 말고 제품 원재료 표시를 반드시 확인하세요."
    )

# --------------------------------------------------
# 스마트팜 및 친환경 먹거리 검색
# --------------------------------------------------
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

# --------------------------------------------------
# BMI 안내
# --------------------------------------------------
elif st.session_state.page == "bmi":
    if st.button("← 홈으로 돌아가기", key="bmi_back"):
        back_home()
        st.rerun()
    st.header("BMI & 성장 정보")
    st.write("BMI는 키와 몸무게를 이용한 참고 지표입니다. 숫자 하나만으로 건강 상태를 판단할 수는 없습니다.")

    st.markdown("""
    <div style="background:linear-gradient(120deg,#29332d,#24211c);border:1px solid #647663;border-radius:10px;padding:1rem 1.2rem;margin:.6rem 0 1rem 0">
      <div style="color:#b7c9ad;font-size:.82rem;letter-spacing:.08em">HOW TO READ BMI</div>
      <div style="font-family:'Noto Serif KR',serif;font-size:1.12rem;color:#f0e8d9;margin:.35rem 0">청소년 BMI는 성인 기준표와 다르게 해석해야 합니다.</div>
      <div style="color:#d4d0c5;font-size:.92rem;line-height:1.65">성장기에는 나이와 성별에 따라 키와 체중의 변화 폭이 다릅니다. 따라서 성인 BMI 구간이나 평균 체중을 목표로 삼지 않고, 연령·성별별 성장도표에서 성장 흐름을 함께 확인해야 합니다.</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("bmi_calculator_form"):
        age_years = st.number_input("만 나이", min_value=2, max_value=100, value=16, step=1)
        sex = st.selectbox("성별 성장도표 선택에 필요한 항목", ["선택 안 함", "남아 성장도표", "여아 성장도표"])
        height_cm = st.number_input("키 (cm)", min_value=80.0, max_value=220.0, value=160.0, step=0.5)
        weight_kg = st.number_input("몸무게 (kg)", min_value=10.0, max_value=200.0, value=50.0, step=0.5)
        submitted = st.form_submit_button("BMI 계산하기", use_container_width=True)

    if submitted:
        if height_cm <= 0 or weight_kg <= 0:
            st.error("키와 몸무게를 올바르게 입력해 주세요.")
        else:
            bmi_value = weight_kg / ((height_cm / 100) ** 2)
            st.metric("계산된 BMI", f"{bmi_value:.1f}")
            if age_years < 20:
                st.info("만 20세 미만은 이 BMI 수치를 성인 기준으로 분류하지 않습니다. 선택한 성별과 정확한 만 나이에 해당하는 공식 성장도표에서 BMI-for-age 백분위수와 성장 추이를 확인해야 합니다.")
                st.caption("현재 앱에는 공식 연령·성별 성장도표 원자료가 연결되어 있지 않아 백분위수나 평균 키·체중을 임의로 표시하지 않습니다. 평균값은 개인의 건강 목표나 적정 체중을 뜻하지 않습니다.")
            else:
                st.info("성인도 BMI는 선별 참고 지표일 뿐입니다. 체성분, 건강 상태, 생활 습관 등을 함께 고려해야 하며 이 앱은 진단이나 체중 목표를 제공하지 않습니다.")

    st.subheader("평균 키·몸무게 정보는 어떻게 볼까요?")
    st.write("연령대별 평균값은 집단의 통계일 뿐 개인에게 적합한 키나 몸무게를 뜻하지 않습니다. 특히 성장기에는 평균과의 차이보다 본인의 성장 곡선이 자연스럽게 이어지는지, 전반적인 건강 상태가 어떤지를 함께 살펴보는 것이 중요합니다.")
    st.caption("정확한 성장 백분위수 확인에는 공식 소아청소년 성장도표의 연령·성별 기준 자료가 필요합니다. 이 앱에서는 검증되지 않은 평균값이나 목표 체중을 만들어 보여주지 않도록 했습니다.")

st.markdown("---")
st.markdown(
    '<div class="footer-brand">THE DINING TABLE · FOOD / NUTRITION / SUSTAINABILITY</div>',
    unsafe_allow_html=True,
)
