```python
import streamlit as st
import pandas as pd
import re
import os
import random


# =========================================================
# 페이지 설정
# =========================================================

st.set_page_config(
    page_title="궁중 식탁 · 식품 영양 분석",
    page_icon="🍚",
    layout="wide"
)


# =========================================================
# 전통 한식 / 궁중 느낌 UI
# =========================================================

st.markdown(
    """
    <style>

    /* 전체 배경 */
    .stApp {
        background:
            linear-gradient(
                rgba(248, 242, 226, 0.94),
                rgba(238, 227, 199, 0.94)
            );
        color: #33281f;
    }

    /* 기본 글씨 */
    html, body, [class*="css"] {
        font-family: "궁서체", "Gungsuh", "BatangChe", serif;
    }

    /* 제목 */
    h1, h2, h3, h4 {
        font-family: "궁서체", "Gungsuh", "BatangChe", serif !important;
        color: #4a2419 !important;
        letter-spacing: 1px;
    }

    /* 일반 텍스트 */
    p, label, div, span {
        font-family: "궁서체", "Gungsuh", "BatangChe", serif;
    }

    /* 메인 타이틀 */
    .royal-title {
        text-align: center;
        padding: 20px 10px 8px 10px;
        color: #54291d;
        font-family: "궁서체", "Gungsuh", serif;
        font-size: 42px;
        font-weight: bold;
        letter-spacing: 4px;
    }

    .royal-subtitle {
        text-align: center;
        color: #745744;
        font-size: 17px;
        margin-bottom: 20px;
    }

    /* 장식선 */
    .royal-line {
        height: 3px;
        background: #8b241c;
        margin: 8px 0 20px 0;
        border-radius: 2px;
    }

    /* 카드 */
    .food-card {
        background: rgba(255, 251, 239, 0.92);
        border: 1px solid #c8ad7f;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 3px 10px rgba(78, 48, 25, 0.08);
    }

    /* 정보 박스 */
    .info-box {
        background: #f5ead0;
        border-left: 5px solid #8b241c;
        padding: 13px 16px;
        border-radius: 5px;
        margin: 10px 0;
    }

    /* 버튼 */
    .stButton > button {
        background-color: #6b281d;
        color: #fffaf0;
        border: 1px solid #4f1d16;
        border-radius: 7px;
        font-family: "궁서체", "Gungsuh", serif;
        font-size: 16px;
    }

    .stButton > button:hover {
        background-color: #8b3326;
        color: white;
    }

    /* 탭 */
    button[data-baseweb="tab"] {
        font-family: "궁서체", "Gungsuh", serif !important;
        color: #5b2b20 !important;
        font-size: 17px !important;
    }

    /* 입력창 */
    input, textarea {
        font-family: "궁서체", "Gungsuh", serif !important;
    }

    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background-color: #eee2c4;
    }

    /* metric */
    [data-testid="stMetric"] {
        background: rgba(255, 250, 237, 0.85);
        border: 1px solid #cdb88e;
        padding: 12px;
        border-radius: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 테스트용 식품 데이터
#
# 나중에 food_data.csv가 생기면 이 데이터 대신 CSV를 사용한다.
# =========================================================

FOOD_DB = {

    # -------------------------
    # 밥 / 주식
    # -------------------------

    "흰밥": {
        "category": "밥류",
        "serving": "100g",
        "unit_g": 100,
        "calories": 130,
        "carbs": 28,
        "sugar": 0.1,
        "protein": 2.7,
        "fat": 0.3,
        "sodium": 1,
        "fiber": 0.4
    },

    "현미밥": {
        "category": "밥류",
        "serving": "100g",
        "unit_g": 100,
        "calories": 111,
        "carbs": 23,
        "sugar": 0.4,
        "protein": 2.6,
        "fat": 0.9,
        "sodium": 1,
        "fiber": 1.8
    },

    "김밥": {
        "category": "밥류",
        "serving": "1줄",
        "unit_g": 250,
        "calories": 450,
        "carbs": 70,
        "sugar": 5,
        "protein": 12,
        "fat": 12,
        "sodium": 900,
        "fiber": 3
    },

    "삼각김밥 참치마요": {
        "category": "편의식",
        "serving": "1개",
        "unit_g": 120,
        "calories": 230,
        "carbs": 34,
        "sugar": 2,
        "protein": 6,
        "fat": 8,
        "sodium": 500,
        "fiber": 1
    },

    # -------------------------
    # 단백질
    # -------------------------

    "닭가슴살": {
        "category": "육류",
        "serving": "100g",
        "unit_g": 100,
        "calories": 165,
        "carbs": 0,
        "sugar": 0,
        "protein": 31,
        "fat": 3.6,
        "sodium": 74,
        "fiber": 0
    },

    "계란": {
        "category": "달걀류",
        "serving": "1개",
        "unit_g": 50,
        "calories": 72,
        "carbs": 0.4,
        "sugar": 0.2,
        "protein": 6.3,
        "fat": 4.8,
        "sodium": 71,
        "fiber": 0
    },

    "두부": {
        "category": "콩류",
        "serving": "100g",
        "unit_g": 100,
        "calories": 76,
        "carbs": 1.9,
        "sugar": 0.5,
        "protein": 8,
        "fat": 4.8,
        "sodium": 7,
        "fiber": 0.3
    },

    "고등어": {
        "category": "생선류",
        "serving": "100g",
        "unit_g": 100,
        "calories": 205,
        "carbs": 0,
        "sugar": 0,
        "protein": 19,
        "fat": 14,
        "sodium": 90,
        "fiber": 0
    },

    "연어": {
        "category": "생선류",
        "serving": "100g",
        "unit_g": 100,
        "calories": 208,
        "carbs": 0,
        "sugar": 0,
        "protein": 20,
        "fat": 13,
        "sodium": 59,
        "fiber": 0
    },

    # -------------------------
    # 채소 / 반찬
    # -------------------------

    "김치": {
        "category": "반찬",
        "serving": "100g",
        "unit_g": 100,
        "calories": 18,
        "carbs": 3.5,
        "sugar": 1.5,
        "protein": 1.1,
        "fat": 0.3,
        "sodium": 550,
        "fiber": 2.4
    },

    "브로콜리": {
        "category": "채소",
        "serving": "100g",
        "unit_g": 100,
        "calories": 34,
        "carbs": 7,
        "sugar": 1.7,
        "protein": 2.8,
        "fat": 0.4,
        "sodium": 33,
        "fiber": 2.6
    },

    "상추": {
        "category": "채소",
        "serving": "50g",
        "unit_g": 50,
        "calories": 8,
        "carbs": 1.5,
        "sugar": 0.5,
        "protein": 0.7,
        "fat": 0.1,
        "sodium": 8,
        "fiber": 0.7
    },

    "방울토마토": {
        "category": "채소",
        "serving": "100g",
        "unit_g": 100,
        "calories": 18,
        "carbs": 3.9,
        "sugar": 2.6,
        "protein": 0.9,
        "fat": 0.2,
        "sodium": 5,
        "fiber": 1.2
    },

    "시금치": {
        "category": "채소",
        "serving": "100g",
        "unit_g": 100,
        "calories": 23,
        "carbs": 3.6,
        "sugar": 0.4,
        "protein": 2.9,
        "fat": 0.4,
        "sodium": 79,
        "fiber": 2.2
    },

    # -------------------------
    # 과일
    # -------------------------

    "바나나": {
        "category": "과일",
        "serving": "1개",
        "unit_g": 100,
        "calories": 89,
        "carbs": 23,
        "sugar": 12,
        "protein": 1.1,
        "fat": 0.3,
        "sodium": 1,
        "fiber": 2.6
    },

    "사과": {
        "category": "과일",
        "serving": "1개",
        "unit_g": 200,
        "calories": 104,
        "carbs": 28,
        "sugar": 21,
        "protein": 0.5,
        "fat": 0.3,
        "sodium": 2,
        "fiber": 4.8
    },

    "딸기": {
        "category": "과일",
        "serving": "100g",
        "unit_g": 100,
        "calories": 32,
        "carbs": 7.7,
        "sugar": 4.9,
        "protein": 0.7,
        "fat": 0.3,
        "sodium": 1,
        "fiber": 2
    },

    # -------------------------
    # 간식
    # -------------------------

    "고구마": {
        "category": "간식/구황작물",
        "serving": "100g",
        "unit_g": 100,
        "calories": 86,
        "carbs": 20,
        "sugar": 4.2,
        "protein": 1.6,
        "fat": 0.1,
        "sodium": 55,
        "fiber": 3
    },

    "감자": {
        "category": "구황작물",
        "serving": "100g",
        "unit_g": 100,
        "calories": 77,
        "carbs": 17,
        "sugar": 0.8,
        "protein": 2,
        "fat": 0.1,
        "sodium": 6,
        "fiber": 2.2
    },

    "요거트": {
        "category": "유제품",
        "serving": "100g",
        "unit_g": 100,
        "calories": 61,
        "carbs": 4.7,
        "sugar": 4.7,
        "protein": 3.5,
        "fat": 3.3,
        "sodium": 46,
        "fiber": 0
    },

    "우유": {
        "category": "유제품",
        "serving": "200ml",
        "unit_g": 200,
        "calories": 122,
        "carbs": 9.4,
        "sugar": 9.4,
        "protein": 6.4,
        "fat": 6.6,
        "sodium": 86,
        "fiber": 0
    },

    # -------------------------
    # 가공식품 / 외식
    # -------------------------

    "라면": {
        "category": "면류",
        "serving": "1봉",
        "unit_g": 120,
        "calories": 500,
        "carbs": 70,
        "sugar": 3,
        "protein": 10,
        "fat": 20,
        "sodium": 1800,
        "fiber": 2
    },

    "샌드위치": {
        "category": "간편식",
        "serving": "1개",
        "unit_g": 180,
        "calories": 350,
        "carbs": 40,
        "sugar": 5,
        "protein": 18,
        "fat": 13,
        "sodium": 700,
        "fiber": 3
    },

    "월남쌈": {
        "category": "간편식",
        "serving": "1개",
        "unit_g": 50,
        "calories": 55,
        "carbs": 8,
        "sugar": 1,
        "protein": 2,
        "fat": 1.5,
        "sodium": 80,
        "fiber": 1
    },

    # -------------------------
    # 디저트
    # -------------------------

    "크리스피 도넛": {
        "category": "디저트",
        "serving": "1개",
        "unit_g": 50,
        "calories": 190,
        "carbs": 22,
        "sugar": 10,
        "protein": 2,
        "fat": 11,
        "sodium": 120,
        "fiber": 1
    },

    "초콜릿 도넛": {
        "category": "디저트",
        "serving": "1개",
        "unit_g": 60,
        "calories": 250,
        "carbs": 30,
        "sugar": 17,
        "protein": 3,
        "fat": 13,
        "sodium": 180,
        "fiber": 1
    },

    "아이스크림": {
        "category": "디저트",
        "serving": "100g",
        "unit_g": 100,
        "calories": 207,
        "carbs": 24,
        "sugar": 21,
        "protein": 3.5,
        "fat": 11,
        "sodium": 80,
        "fiber": 0
    },

    # -------------------------
    # 음료
    # -------------------------

    "아메리카노": {
        "category": "음료",
        "serving": "355ml",
        "unit_g": 355,
        "calories": 10,
        "carbs": 1,
        "sugar": 0,
        "protein": 0.5,
        "fat": 0,
        "sodium": 5,
        "fiber": 0
    },

    "카페라떼": {
        "category": "음료",
        "serving": "355ml",
        "unit_g": 355,
        "calories": 180,
        "carbs": 18,
        "sugar": 15,
        "protein": 9,
        "fat": 7,
        "sodium": 120,
        "fiber": 0
    }
}


# =========================================================
# CSV가 존재하면 자동으로 읽는 함수
# =========================================================

def load_food_data():

    csv_path = "food_data.csv"

    if not os.path.exists(csv_path):
        return FOOD_DB

    try:

        df = pd.read_csv(
            csv_path,
            encoding="utf-8-sig"
        )

        required_columns = [
            "식품명",
            "중량(g)",
            "칼로리(kcal)",
            "탄수화물(g)",
            "단백질(g)",
            "지방(g)",
            "나트륨(mg)"
        ]

        if not all(
            column in df.columns
            for column in required_columns
        ):
            return FOOD_DB

        new_db = {}

        for _, row in df.iterrows():

            name = str(
                row["식품명"]
            ).strip()

            if not name:
                continue

            try:

                weight = float(
                    row["중량(g)"]
                )

                new_db[name] = {

                    "category":
                        str(
                            row.get(
                                "식품분류",
                                "기타"
                            )
                        ),

                    "serving":
                        str(
                            row.get(
                                "1회 제공량",
                                f"{weight}g"
                            )
                        ),

                    "unit_g": weight,

                    "calories":
                        float(
                            row["칼로리(kcal)"]
                        ),

                    "carbs":
                        float(
                            row["탄수화물(g)"]
                        ),

                    "sugar":
                        float(
                            row.get(
                                "당류(g)",
                                0
                            )
                        ),

                    "protein":
                        float(
                            row["단백질(g)"]
                        ),

                    "fat":
                        float(
                            row["지방(g)"]
                        ),

                    "sodium":
                        float(
                            row["나트륨(mg)"]
                        ),

                    "fiber":
                        float(
                            row.get(
                                "식이섬유(g)",
                                0
                            )
                        )
                }

            except (ValueError, TypeError):
                continue

        if new_db:
            return new_db

    except Exception:
        pass

    return FOOD_DB


FOOD_DB = load_food_data()


# =========================================================
# 세션 상태
# =========================================================

if "intake_list" not in st.session_state:
    st.session_state.intake_list = []


# =========================================================
# 섭취량 해석 함수
# =========================================================

def parse_amount(text, food_name):

    text = text.strip().lower()

    food = FOOD_DB[food_name]

    # g
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(g|그램)",
        text
    )

    if match:
        return float(match.group(1))

    # kg
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(kg|킬로그램)",
        text
    )

    if match:
        return float(match.group(1)) * 1000

    # 공기
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*공기",
        text
    )

    if match:

        number = float(match.group(1))

        if food_name in ["흰밥", "현미밥"]:
            return number * 210

        return number * food["unit_g"]

    # 반 공기
    if "반공기" in text or "반 공기" in text:

        if food_name in ["흰밥", "현미밥"]:
            return 105

        return food["unit_g"] * 0.5

    # 한 공기
    if "한공기" in text or "한 공기" in text:

        if food_name in ["흰밥", "현미밥"]:
            return 210

        return food["unit_g"]

    # 한 주먹
    if (
        "한주먹" in text
        or "한 주먹" in text
        or "주먹만큼" in text
        or "주먹 만큼" in text
    ):
        return 100

    # 주먹의 반
    if (
        "주먹의 반" in text
        or "주먹 반" in text
        or "주먹의 절반" in text
    ):
        return 50

    # 한 줌
    if (
        "한줌" in text
        or "한 줌" in text
    ):
        return 30

    # 반 개
    if "반개" in text or "반 개" in text:
        return food["unit_g"] * 0.5

    # 숫자 + 개/알/봉/팩/컵/잔
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(개|알|봉|팩|컵|잔|장|줄)",
        text
    )

    if match:

        number = float(match.group(1))

        return number * food["unit_g"]

    # 한 개
    if (
        "한개" in text
        or "한 개" in text
        or "하나" in text
    ):
        return food["unit_g"]

    # 한 잔
    if "한잔" in text or "한 잔" in text:
        return food["unit_g"]

    # 숫자만
    match = re.search(
        r"(\d+(?:\.\d+)?)",
        text
    )

    if match:
        return float(match.group(1))

    return None


# =========================================================
# 음식 검색
# =========================================================

def search_food(keyword):

    keyword = keyword.strip().lower()

    if not keyword:
        return list(FOOD_DB.keys())

    results = []

    for food_name in FOOD_DB.keys():

        if keyword in food_name.lower():
            results.append(food_name)

    return results


# =========================================================
# 영양 계산
# =========================================================

def calculate_nutrition(food_name, amount):

    food = FOOD_DB[food_name]

    ratio = amount / food["unit_g"]

    return {

        "음식":
            food_name,

        "섭취량(g)":
            round(amount, 1),

        "칼로리(kcal)":
            round(
                food["calories"] * ratio,
                1
            ),

        "탄수화물(g)":
            round(
                food["carbs"] * ratio,
                1
            ),

        "당류(g)":
            round(
                food["sugar"] * ratio,
                1
            ),

        "단백질(g)":
            round(
                food["protein"] * ratio,
                1
            ),

        "지방(g)":
            round(
                food["fat"] * ratio,
                1
            ),

        "나트륨(mg)":
            round(
                food["sodium"] * ratio,
                1
            ),

        "식이섬유(g)":
            round(
                food["fiber"] * ratio,
                1
            )
    }


# =========================================================
# 자연어에서 음식 찾기
# =========================================================

def find_food_in_text(text):

    # 긴 음식명을 먼저 검색
    food_names = sorted(
        FOOD_DB.keys(),
        key=len,
        reverse=True
    )

    for food_name in food_names:

        if food_name.lower() in text.lower():

            return food_name

    return None


# =========================================================
# 여러 음식 입력 처리
# =========================================================

def parse_multiple_foods(text):

    # 쉼표, 그리고, 및 등으로 분리
    parts = re.split(
        r",|\n|그리고|및",
        text
    )

    results = []
    errors = []

    for part in parts:

        part = part.strip()

        if not part:
            continue

        food_name = find_food_in_text(part)

        if food_name is None:

            errors.append(part)
            continue

        amount = parse_amount(
            part,
            food_name
        )

        if amount is None:

            errors.append(part)
            continue

        result = calculate_nutrition(
            food_name,
            amount
        )

        result["입력 내용"] = part

        results.append(result)

    return results, errors


# =========================================================
# 총 영양성분
# =========================================================

def calculate_total():

    if not st.session_state.intake_list:

        return {
            "칼로리(kcal)": 0,
            "탄수화물(g)": 0,
            "당류(g)": 0,
            "단백질(g)": 0,
            "지방(g)": 0,
            "나트륨(mg)": 0,
            "식이섬유(g)": 0
        }

    df = pd.DataFrame(
        st.session_state.intake_list
    )

    return {

        "칼로리(kcal)":
            round(
                df["칼로리(kcal)"].sum(),
                1
            ),

        "탄수화물(g)":
            round(
                df["탄수화물(g)"].sum(),
                1
            ),

        "당류(g)":
            round(
                df["당류(g)"].sum(),
                1
            ),

        "단백질(g)":
            round(
                df["단백질(g)"].sum(),
                1
            ),

        "지방(g)":
            round(
                df["지방(g)"].sum(),
                1
            ),

        "나트륨(mg)":
            round(
                df["나트륨(mg)"].sum(),
                1
            ),

        "식이섬유(g)":
            round(
                df["식이섬유(g)"].sum(),
                1
            )
    }


# =========================================================
# 일반 영양 참고값
# =========================================================

def get_general_targets():

    return {

        "칼로리": 2300,
        "탄수화물": 330,
        "단백질": 55,
        "지방": 75,
        "나트륨": 2000,
        "식이섬유": 25

    }


# =========================================================
# 식단 추천용 음식 분류
# =========================================================

MEAL_GROUPS = {

    "주식": [
        "흰밥",
        "현미밥",
        "김밥"
    ],

    "단백질": [
        "닭가슴살",
        "계란",
        "두부",
        "고등어",
        "연어"
    ],

    "채소": [
        "브로콜리",
        "상추",
        "방울토마토",
        "시금치"
    ],

    "반찬": [
        "김치"
    ],

    "과일": [
        "바나나",
        "사과",
        "딸기"
    ],

    "유제품": [
        "우유",
        "요거트"
    ],

    "간식": [
        "고구마",
        "아이스크림",
        "크리스피 도넛",
        "초콜릿 도넛"
    ]
}


# =========================================================
# 실제 음식 조합
# =========================================================

def create_meal(meal_type, preference):

    meal = []

    # 주식
    if meal_type in ["아침", "점심", "저녁"]:

        if preference == "가볍게":

            main = random.choice(
                ["현미밥", "고구마"]
            )

        else:

            main = random.choice(
                MEAL_GROUPS["주식"]
            )

        meal.append(main)

    # 단백질
    protein = random.choice(
        MEAL_GROUPS["단백질"]
    )

    meal.append(protein)

    # 채소 1~2개
    vegetables = random.sample(
        MEAL_GROUPS["채소"],
        k=2
    )

    meal.extend(vegetables)

    # 반찬
    if "김치" in FOOD_DB:

        meal.append("김치")

    # 아침이면 유제품 또는 과일
    if meal_type == "아침":

        extra = random.choice(
            MEAL_GROUPS["과일"]
            + MEAL_GROUPS["유제품"]
        )

        meal.append(extra)

    # 점심이면 과일
    elif meal_type == "점심":

        meal.append(
            random.choice(
                MEAL_GROUPS["과일"]
            )
        )

    # 저녁이면 과일/유제품 중 하나
    else:

        meal.append(
            random.choice(
                MEAL_GROUPS["과일"]
            )
        )

    return meal


# =========================================================
# 메인 화면
# =========================================================

st.markdown(
    """
    <div class="royal-title">
        🍚 궁중 식탁
    </div>

    <div class="royal-subtitle">
        식품 영양 성분 분석 · 섭취 기록 · 맞춤 식단 관리
    </div>

    <div class="royal-line"></div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="info-box">
    오늘 먹은 음식을 기록하고, 음식에 포함된 영양성분을
    한눈에 확인해보세요.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 사이드바
# =========================================================

st.sidebar.title("👤 나의 정보")

age = st.sidebar.number_input(
    "나이",
    min_value=10,
    max_value=100,
    value=17
)

height = st.sidebar.number_input(
    "키(cm)",
    min_value=100.0,
    max_value=220.0,
    value=165.0
)

weight = st.sidebar.number_input(
    "몸무게(kg)",
    min_value=25.0,
    max_value=150.0,
    value=60.0
)

activity = st.sidebar.selectbox(
    "평소 활동량",
    [
        "낮음",
        "보통",
        "높음"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    f"현재 식품 데이터: {len(FOOD_DB)}개"
)

if os.path.exists("food_data.csv"):

    st.sidebar.success(
        "food_data.csv가 연결되었습니다."
    )

else:

    st.sidebar.info(
        "현재는 테스트용 식품 데이터를 사용합니다."
    )


# =========================================================
# 탭
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🔎 음식 검색",
        "🍽️ 섭취 기록",
        "📊 영양 분석",
        "🥢 식단 만들기"
    ]
)


# =========================================================
# TAB 1
# 음식 검색
# =========================================================

with tab1:

    st.header("🔎 음식 검색")

    search = st.text_input(
        "음식 이름을 검색하세요.",
        placeholder="예: 크리스피 도넛 / 닭가슴살 / 계란 / 라떼"
    )

    if search:

        results = search_food(search)

        if results:

            st.success(
                f"{len(results)}개의 음식을 찾았습니다."
            )

            for food_name in results:

                food = FOOD_DB[food_name]

                with st.container():

                    st.markdown(
                        f"""
                        <div class="food-card">
                            <h3>🍽️ {food_name}</h3>
                            <p>
                            분류: {food["category"]}<br>
                            기준 제공량: {food["serving"]}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    c1, c2, c3, c4 = st.columns(4)

                    with c1:
                        st.metric(
                            "칼로리",
                            f"{food['calories']} kcal"
                        )

                    with c2:
                        st.metric(
                            "탄수화물",
                            f"{food['carbs']} g"
                        )

                    with c3:
                        st.metric(
                            "단백질",
                            f"{food['protein']} g"
                        )

                    with c4:
                        st.metric(
                            "지방",
                            f"{food['fat']} g"
                        )

                    c5, c6, c7 = st.columns(3)

                    with c5:
                        st.metric(
                            "당류",
                            f"{food['sugar']} g"
                        )

                    with c6:
                        st.metric(
                            "나트륨",
                            f"{food['sodium']} mg"
                        )

                    with c7:
                        st.metric(
                            "식이섬유",
                            f"{food['fiber']} g"
                        )

                    st.divider()

        else:

            st.warning(
                "해당 음식이 현재 데이터에 없습니다."
            )

            st.info(
                "나중에 food_data.csv에 식품을 추가하면 "
                "검색할 수 있습니다."
            )

    else:

        st.write(
            "예를 들어 `크리스피`, `도넛`, `닭가슴살`처럼 "
            "음식 이름의 일부만 검색해도 됩니다."
        )


# =========================================================
# TAB 2
# 섭취 기록
# =========================================================

with tab2:

    st.header("🍽️ 오늘 먹은 음식 기록")

    st.write(
        "먹은 음식을 자연스럽게 입력해보세요."
    )

    st.markdown(
        """
        <div class="info-box">
        <b>입력 예시</b><br>
        닭가슴살 150g, 계란 2개, 밥 1공기, 김치 한 줌
        </div>
        """,
        unsafe_allow_html=True
    )

    intake_text = st.text_area(
        "섭취한 음식",
        placeholder=(
            "예: 닭가슴살 150g, 계란 2개, "
            "밥 1공기, 김치 한 줌"
        ),
        height=100
    )

    if st.button(
        "🍽️ 섭취량 분석하기",
        use_container_width=True
    ):

        if not intake_text.strip():

            st.warning(
                "먹은 음식을 입력해주세요."
            )

        else:

            results, errors = parse_multiple_foods(
                intake_text
            )

            if results:

                st.subheader(
                    "🔎 입력 내용 분석 결과"
                )

                for result in results:

                    st.write(
                        f"**{result['입력 내용']}**"
                        f" → {result['음식']} "
                        f"{result['섭취량(g)']}g"
                    )

                st.divider()

                # 중복 기록 방지
                for result in results:

                    saved = result.copy()

                    saved.pop(
                        "입력 내용",
                        None
                    )

                    st.session_state.intake_list.append(
                        saved
                    )

                st.success(
                    f"{len(results)}개의 음식이 "
                    "섭취 기록에 추가되었습니다."
                )

            if errors:

                st.warning(
                    "다음 입력은 인식하지 못했습니다: "
                    + ", ".join(errors)
                )

                st.caption(
                    "현재 데이터에 없는 음식이거나 "
                    "섭취량 표현을 이해하지 못했을 수 있습니다."
                )

    st.divider()

    st.subheader(
        "📋 오늘의 섭취 기록"
    )

    if st.session_state.intake_list:

        df = pd.DataFrame(
            st.session_state.intake_list
        )

        display_columns = [
            "음식",
            "섭취량(g)",
            "칼로리(kcal)",
            "탄수화물(g)",
            "당류(g)",
            "단백질(g)",
            "지방(g)",
            "나트륨(mg)",
            "식이섬유(g)"
        ]

        st.dataframe(
            df[display_columns],
            use_container_width=True,
            hide_index=True
        )

        if st.button(
            "🗑️ 오늘의 기록 전체 삭제"
        ):

            st.session_state.intake_list = []

            st.rerun()

    else:

        st.info(
            "아직 오늘의 섭취 기록이 없습니다."
        )


# =========================================================
# TAB 3
# 영양 분석
# =========================================================

with tab3:

    st.header("📊 오늘의 영양 분석")

    total = calculate_total()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "칼로리",
            f"{total['칼로리(kcal)']} kcal"
        )

    with c2:
        st.metric(
            "탄수화물",
            f"{total['탄수화물(g)']} g"
        )

    with c3:
        st.metric(
            "단백질",
            f"{total['단백질(g)']} g"
        )

    c4, c5, c6 = st.columns(3)

    with c4:
        st.metric(
            "지방",
            f"{total['지방(g)']} g"
        )

    with c5:
        st.metric(
            "당류",
            f"{total['당류(g)']} g"
        )

    with c6:
        st.metric(
            "식이섬유",
            f"{total['식이섬유(g)']} g"
        )

    st.divider()

    st.subheader(
        "📈 영양소별 섭취량"
    )

    chart_data = pd.DataFrame(
        {
            "영양소": [
                "탄수화물",
                "단백질",
                "지방",
                "당류",
                "식이섬유"
            ],
            "섭취량(g)": [
                total["탄수화물(g)"],
                total["단백질(g)"],
                total["지방(g)"],
                total["당류(g)"],
                total["식이섬유(g)"]
            ]
        }
    )

    st.bar_chart(
        chart_data.set_index("영양소")
    )

    st.subheader(
        "🧂 나트륨 섭취량"
    )

    st.progress(
        min(
            total["나트륨(mg)"] / 2000,
            1.0
        )
    )

    st.write(
        f"현재 기록된 나트륨: "
        f"**{total['나트륨(mg)']} mg**"
    )

    st.caption(
        "영양 기준은 일반적인 비교를 위한 참고값이며, "
        "개인의 의료적·영양학적 처방을 대신하지 않습니다."
    )


# =========================================================
# TAB 4
# 식단 만들기
# =========================================================

with tab4:

    st.header("🥢 맞춤 식단 만들기")

    st.write(
        "한 끼를 여러 종류의 음식으로 구성하여 "
        "조금 더 실제 식사에 가까운 식단을 만들어봅니다."
    )

    c1, c2 = st.columns(2)

    with c1:

        meal_days = st.slider(
            "식단 기간",
            1,
            7,
            3
        )

    with c2:

        preference = st.selectbox(
            "식단 스타일",
            [
                "균형 있게",
                "가볍게",
                "한식 중심",
                "좋아하는 음식을 포함"
            ]
        )

    meal_choices = st.multiselect(
        "식단을 만들 식사",
        [
            "아침",
            "점심",
            "저녁",
            "간식"
        ],
        default=[
            "아침",
            "점심",
            "저녁"
        ]
    )

    if st.button(
        "🥢 식단 생성하기",
        use_container_width=True
    ):

        if not meal_choices:

            st.warning(
                "최소 한 가지 식사를 선택해주세요."
            )

        else:

            for day in range(
                1,
                meal_days + 1
            ):

                st.subheader(
                    f"📜 {day}일차 식단"
                )

                for meal_type in meal_choices:

                    if meal_type == "간식":

                        snack = random.choice(
                            MEAL_GROUPS["간식"]
                        )

                        st.markdown(
                            f"**🍵 간식**"
                        )

                        st.write(
                            f"• {snack}"
                        )

                        continue

                    meal = create_meal(
                        meal_type,
                        preference
                    )

                    st.markdown(
                        f"**🍚 {meal_type}**"
                    )

                    st.write(
                        " · ".join(meal)
                    )

                    # 해당 식단의 대략적인 영양값
                    calories = 0
                    protein = 0
                    carbs = 0

                    for food_name in meal:

                        if food_name not in FOOD_DB:
                            continue

                        food = FOOD_DB[
                            food_name
                        ]

                        calories += food["calories"]
                        protein += food["protein"]
                        carbs += food["carbs"]

                    st.caption(
                        f"구성 예시 기준 약 "
                        f"{calories:.0f} kcal · "
                        f"탄수화물 {carbs:.1f}g · "
                        f"단백질 {protein:.1f}g"
                    )

                st.divider()


# =========================================================
# 하단 안내
# =========================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#755b48;
        padding:20px;
        font-size:15px;
    ">
    🍚 궁중 식탁 · Food Nutrition Analysis<br>
    식품 영양정보 확인 및 식단 계획을 위한 참고용 프로그램
    </div>
    """,
    unsafe_allow_html=True
)
```
