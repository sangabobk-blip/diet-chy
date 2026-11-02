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
    page_icon="🍽️",
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
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Noto+Sans+KR:wght@400;500;600;700&display=swap');
:root {
    --bg: #171310; --panel: #241d17; --gold: #c8a66b;
    --line: #59452f; --text: #eee6da; --muted: #b9a995;
}
html, body, [class*="css"], button, input, textarea, select,
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] {
    font-family: 'Noto Sans KR', sans-serif !important;
}
body, p, li, label, input, textarea, select, button { letter-spacing: -.01em; }
.stApp { background: var(--bg); color: var(--text); }
[data-testid="stHeader"] { background: rgba(23,19,16,.92); }
.block-container { max-width: 1180px; padding-top: 1.2rem; padding-bottom: 2.5rem; }
h1,h2,h3,h4,h5,h6 { color: #f1e5d3 !important; font-weight: 600 !important; }
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
[data-testid="stMetric"] { background: var(--panel); border: 1px solid var(--line); border-radius: 4px; padding: .7rem; }
[data-testid="stMetricLabel"] { color: var(--muted) !important; }
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

def food_label(catalog_id):
    row = CATALOG.loc[CATALOG["catalog_id"] == catalog_id].iloc[0]
    return f'{row["food_name"]} · {row["catalog_type"]}'

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

# --------------------------------------------------
# 사이드바
# --------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-brand">THE DINING TABLE</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-kicker">FOOD · NUTRITION · SUSTAINABILITY</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="sidebar-section-label">Explore</div>', unsafe_allow_html=True)
    nav_items = [
        ("🏠 홈으로", "home", "nav_home"),
        ("🥗 영양 성분 분석", "nutrition", "nav_nutrition"),
        ("🍱 맞춤형 식단", "meal", "nav_meal"),
        ("👤 사용자 영양 설정", "profile", "nav_profile"),
        ("🌱 스마트팜 검색", "farm", "nav_farm"),
        ("📊 BMI 안내", "bmi", "nav_bmi"),
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
              <a class="kitchen-hotspot hotspot-nutrition" href="?page=nutrition" target="_top"><span>🥗 영양 성분 분석</span></a>
              <a class="kitchen-hotspot hotspot-meal" href="?page=meal" target="_top"><span>🍱 맞춤형 식단</span></a>
              <a class="kitchen-hotspot hotspot-bmi" href="?page=bmi" target="_top"><span>📊 BMI 안내</span></a>
              <a class="kitchen-hotspot hotspot-farm" href="?page=farm" target="_top"><span>🌱 스마트팜 검색</span></a>
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
                unit = basis_unit(candidate["nutrient_basis"])
                amount = st.number_input(
                    f"섭취량 ({unit})",
                    min_value=1.0,
                    max_value=5000.0,
                    value=100.0,
                    step=10.0,
                    key="nutrition_amount",
                )
                values, _, basis = nutrient_values(candidate, amount)
                st.caption(f'영양성분 자료: {candidate["nutrition_food_name"]} · 기준량: {basis} · 자료 구분: {candidate["nutrition_data_type"]}')
                show_nutrients(values)
                with st.expander("영양성분 자세히 보기"):
                    detail_keys = list(NUTRIENTS.keys())
                    detail = [
                        {"영양성분": NUTRIENTS[k][0], "섭취량 기준 계산값": round(values[k], 2)}
                        for k in detail_keys
                    ]
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
# 맞춤형 식단: 사용자가 고른 식품의 영양성분 합산
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
    st.write("기간과 식품 종류를 선택해 여러 날의 식단을 구성해 보세요.")

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
        st.info("알레르기 설정은 자동 추천 후보를 걸러내는 보조 기능입니다. 실제 제품의 원재료와 교차접촉 정보는 반드시 별도로 확인하세요.")

        category_values = sorted(
            [str(x) for x in CATALOG["food_category"].dropna().unique() if str(x).strip()]
        )
        base_options = search_catalog(
            "", CATALOG, limit=5000, nutrition_only=True
        ).copy()

        # 식품명에 알레르기 키워드가 포함된 후보를 자동 추천에서 제외
        allergy_words = [str(x).replace(" ", "").casefold() for x in profile["allergies"]]
        def allergy_filtered(frame):
            if not allergy_words:
                return frame
            names = frame["food_name"].fillna("").map(normalize_food_name)
            blocked = pd.Series(False, index=frame.index)
            for word in allergy_words:
                blocked |= names.str.contains(re.escape(normalize_food_name(word)), na=False)
            return frame[~blocked].copy()

        all_day_totals = []
        plan_detail_rows = []

        for day_number in range(1, meal_days + 1):
            st.subheader(f"{day_number}일차")
            day_totals = {key: 0.0 for key in NUTRIENTS}

            for meal_name in ["아침", "점심", "저녁"]:
                with st.expander(f"{meal_name} 식단", expanded=(day_number == 1 and meal_name == "아침")):
                    category_key = f"meal_cat_{day_number}_{meal_name}"
                    category = st.selectbox(
                        f"{meal_name} 식품 카테고리",
                        ["전체 카테고리"] + category_values,
                        key=category_key,
                    )
                    search_text = st.text_input(
                        f"{meal_name} 식품 검색",
                        placeholder="예: 밥, 달걀, 사과",
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
                    meal_options = allergy_filtered(meal_options)

                    option_ids = meal_options["catalog_id"].tolist()
                    selection_key = f"meal_selected_{day_number}_{meal_name}"

                    if st.button(
                        f"✨ {meal_name} 자동 구성",
                        key=f"auto_meal_{day_number}_{meal_name}",
                        help="현재 카테고리와 알레르기 설정을 참고해 식품 후보를 골라 줍니다.",
                    ):
                        if not option_ids:
                            st.warning("선택 조건에 맞는 식품이 없습니다. 카테고리나 검색어를 바꿔 보세요.")
                        else:
                            # 카테고리 필터가 있으면 해당 카테고리 안에서, 없으면 전체에서 선택
                            chosen = meal_options["catalog_id"].head(3).tolist()
                            st.session_state[selection_key] = chosen

                    selected_ids = st.multiselect(
                        f"{meal_name}에 넣을 식품",
                        option_ids,
                        format_func=food_label,
                        key=selection_key,
                        help="여러 식품을 선택할 수 있습니다. 자동 구성 후 직접 수정해도 됩니다.",
                    )

                    quantities = []
                    for food_id in selected_ids:
                        candidate_rows = linked_rows(food_id)
                        default_unit = (
                            basis_unit(candidate_rows.iloc[0]["nutrient_basis"])
                            if not candidate_rows.empty else "g"
                        )
                        amount = st.number_input(
                            f"{food_label(food_id)} 섭취량 ({default_unit})",
                            min_value=1.0,
                            max_value=5000.0,
                            value=100.0,
                            step=10.0,
                            key=f"meal_amount_{day_number}_{meal_name}_{food_id}",
                        )
                        quantities.append(amount)

                    if selected_ids:
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
                        st.caption("아직 선택한 식품이 없습니다.")

            all_day_totals.append((day_number, day_totals))
            st.markdown(f"**{day_number}일차 하루 합계**")
            show_nutrients(day_totals)

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
            st.info("다운로드하려면 먼저 식단에 식품을 추가해 주세요.")

        st.download_button(
            "기간별 영양 요약 다운로드 (CSV)",
            data=summary_df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"영양요약_{meal_days}일.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_meal_summary",
        )

    st.caption(
        "식단은 식품을 기록하고 영양 정보를 살펴보는 참고 도구입니다. "
        "성장기에는 특정 수치에 맞추어 식사를 제한하기보다 다양한 식품을 균형 있게 먹는 것이 중요합니다."
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
    st.header("BMI Calculator")
    st.write(
        "키와 몸무게를 입력하면 참고용 BMI 수치를 계산합니다. "
        "BMI는 건강 상태를 단독으로 판단하는 기준이 아닙니다."
    )

    st.info(
        "청소년은 성장 단계와 연령·성별에 따른 성장 기준을 함께 살펴야 합니다. "
        "따라서 성인용 BMI 구간이나 목표 BMI·목표 체중을 적용하지 않습니다."
    )

    with st.form("bmi_calculator_form"):
        height_cm = st.number_input(
            "키 (cm)", min_value=80.0, max_value=220.0,
            value=160.0, step=0.5
        )
        weight_kg = st.number_input(
            "몸무게 (kg)", min_value=10.0, max_value=200.0,
            value=50.0, step=0.5
        )
        submitted = st.form_submit_button("BMI 계산하기", use_container_width=True)

    if submitted:
        if height_cm <= 0 or weight_kg <= 0:
            st.error("키와 몸무게를 올바르게 입력해 주세요.")
        else:
            height_m = height_cm / 100
            bmi_value = weight_kg / (height_m ** 2)
            st.metric("계산된 BMI", f"{bmi_value:.1f}")
            st.caption(
                "이 숫자만으로 저체중·정상·과체중 여부를 판단하거나 "
                "체중 목표를 정하지 마세요. 청소년의 성장 상태는 "
                "보호자와 의료 전문가가 연령·성별별 성장도표 및 건강 정보를 "
                "함께 확인하는 것이 적절합니다."
            )

    st.markdown("#### 건강 목표 설정")
    st.write(
        "BMI 숫자를 목표로 삼기보다 규칙적인 식사, 다양한 식품 섭취, "
        "충분한 수면과 일상적인 신체활동처럼 건강을 돕는 습관을 살펴보세요."
    )

st.markdown("---")
st.markdown(
    '<div class="footer-brand">THE DINING TABLE · FOOD / NUTRITION / SUSTAINABILITY</div>',
    unsafe_allow_html=True,
)
