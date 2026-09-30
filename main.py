
import streamlit as st
import pandas as pd
import re


# =========================================================
# 페이지 설정
# =========================================================

st.set_page_config(
    page_title="식품 영양 성분 분석 & 맞춤형 식단 관리",
    page_icon="🥗",
    layout="wide"
)


# =========================================================
# 기본 음식 데이터
# 현재는 테스트용 데이터
# 추후 food_data.csv의 공공데이터로 교체
# =========================================================

FOOD_DB = {

    "닭가슴살": {
        "serving": "100g",
        "unit_g": 100,
        "calories": 165,
        "carbs": 0,
        "protein": 31,
        "fat": 3.6,
        "sodium": 74,
        "fiber": 0
    },

    "흰밥": {
        "serving": "100g",
        "unit_g": 100,
        "calories": 130,
        "carbs": 28,
        "protein": 2.7,
        "fat": 0.3,
        "sodium": 1,
        "fiber": 0.4
    },

    "현미밥": {
        "serving": "100g",
        "unit_g": 100,
        "calories": 111,
        "carbs": 23,
        "protein": 2.6,
        "fat": 0.9,
        "sodium": 1,
        "fiber": 1.8
    },

    "계란": {
        "serving": "1개",
        "unit_g": 50,
        "calories": 72,
        "carbs": 0.4,
        "protein": 6.3,
        "fat": 4.8,
        "sodium": 71,
        "fiber": 0
    },

    "고등어": {
        "serving": "100g",
        "unit_g": 100,
        "calories": 205,
        "carbs": 0,
        "protein": 19,
        "fat": 14,
        "sodium": 90,
        "fiber": 0
    },

    "연어": {
        "serving": "100g",
        "unit_g": 100,
        "calories": 208,
        "carbs": 0,
        "protein": 20,
        "fat": 13,
        "sodium": 59,
        "fiber": 0
    },

    "두부": {
        "serving": "100g",
        "unit_g": 100,
        "calories": 76,
        "carbs": 1.9,
        "protein": 8,
        "fat": 4.8,
        "sodium": 7,
        "fiber": 0.3
    },

    "바나나": {
        "serving": "1개",
        "unit_g": 100,
        "calories": 89,
        "carbs": 23,
        "protein": 1.1,
        "fat": 0.3,
        "sodium": 1,
        "fiber": 2.6
    },

    "사과": {
        "serving": "1개",
        "unit_g": 200,
        "calories": 104,
        "carbs": 28,
        "protein": 0.5,
        "fat": 0.3,
        "sodium": 2,
        "fiber": 4.8
    },

    "고구마": {
        "serving": "100g",
        "unit_g": 100,
        "calories": 86,
        "carbs": 20,
        "protein": 1.6,
        "fat": 0.1,
        "sodium": 55,
        "fiber": 3
    },

    "감자": {
        "serving": "100g",
        "unit_g": 100,
        "calories": 77,
        "carbs": 17,
        "protein": 2,
        "fat": 0.1,
        "sodium": 6,
        "fiber": 2.2
    },

    "우유": {
        "serving": "200ml",
        "unit_g": 200,
        "calories": 122,
        "carbs": 9.4,
        "protein": 6.4,
        "fat": 6.6,
        "sodium": 86,
        "fiber": 0
    },

    "요거트": {
        "serving": "100g",
        "unit_g": 100,
        "calories": 61,
        "carbs": 4.7,
        "protein": 3.5,
        "fat": 3.3,
        "sodium": 46,
        "fiber": 0
    },

    "라면": {
        "serving": "1봉",
        "unit_g": 120,
        "calories": 500,
        "carbs": 70,
        "protein": 10,
        "fat": 20,
        "sodium": 1800,
        "fiber": 2
    },

    "김치": {
        "serving": "100g",
        "unit_g": 100,
        "calories": 18,
        "carbs": 3.5,
        "protein": 1.1,
        "fat": 0.3,
        "sodium": 550,
        "fiber": 2.4
    },

    "월남쌈": {
        "serving": "1개",
        "unit_g": 50,
        "calories": 55,
        "carbs": 8,
        "protein": 2,
        "fat": 1.5,
        "sodium": 80,
        "fiber": 1
    },

    "샌드위치": {
        "serving": "1개",
        "unit_g": 180,
        "calories": 350,
        "carbs": 40,
        "protein": 18,
        "fat": 13,
        "sodium": 700,
        "fiber": 3
    }
}


# =========================================================
# 세션 상태
# =========================================================

if "intake_list" not in st.session_state:
    st.session_state.intake_list = []


# =========================================================
# 영양성분 계산 함수
# =========================================================

def calculate_nutrition(food_name, amount):
    """
    실제 섭취량을 기준으로 영양성분 계산
    """

    food = FOOD_DB[food_name]

    ratio = amount / food["unit_g"]

    return {
        "음식": food_name,
        "섭취량": round(amount, 1),
        "칼로리(kcal)": round(
            food["calories"] * ratio, 1
        ),
        "탄수화물(g)": round(
            food["carbs"] * ratio, 1
        ),
        "단백질(g)": round(
            food["protein"] * ratio, 1
        ),
        "지방(g)": round(
            food["fat"] * ratio, 1
        ),
        "나트륨(mg)": round(
            food["sodium"] * ratio, 1
        ),
        "식이섬유(g)": round(
            food["fiber"] * ratio, 1
        )
    }


# =========================================================
# 자연어 섭취량 해석
# =========================================================

def parse_amount(text, food_name):

    """
    사용자의 자연어 섭취량을 g 단위로 변환한다.

    지원 예시

    150g
    150 g
    150그램

    2개
    2알
    1봉
    1팩

    1공기
    반 공기

    한 주먹
    주먹의 반

    한 줌

    숫자만 입력
    """

    text = text.strip().lower()

    food = FOOD_DB[food_name]


    # -----------------------------------------------------
    # 1. g
    # -----------------------------------------------------

    gram_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(g|그램)",
        text
    )

    if gram_match:

        return float(
            gram_match.group(1)
        )


    # -----------------------------------------------------
    # 2. kg
    # -----------------------------------------------------

    kg_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(kg|킬로그램)",
        text
    )

    if kg_match:

        return (
            float(kg_match.group(1))
            * 1000
        )


    # -----------------------------------------------------
    # 3. 개 / 알 / 봉 / 팩 / 컵 / 잔
    # -----------------------------------------------------

    count_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(개|알|봉|팩|컵|잔)",
        text
    )

    if count_match:

        count = float(
            count_match.group(1)
        )

        return count * food["unit_g"]


    # -----------------------------------------------------
    # 4. 숫자 + 공기
    # -----------------------------------------------------

    bowl_match = re.search(
        r"(\d+(?:\.\d+)?)\s*공기",
        text
    )

    if bowl_match:

        bowl = float(
            bowl_match.group(1)
        )

        # 밥 1공기 약 210g
        if food_name in [
            "흰밥",
            "현미밥"
        ]:

            return bowl * 210

        return bowl * food["unit_g"]


    # -----------------------------------------------------
    # 5. 반 공기
    # -----------------------------------------------------

    if (
        "반 공기" in text
        or "반공기" in text
    ):

        if food_name in [
            "흰밥",
            "현미밥"
        ]:

            return 105

        return food["unit_g"] * 0.5


    # -----------------------------------------------------
    # 6. 한 공기
    # -----------------------------------------------------

    if (
        "한 공기" in text
        or "한공기" in text
    ):

        if food_name in [
            "흰밥",
            "현미밥"
        ]:

            return 210

        return food["unit_g"]


    # -----------------------------------------------------
    # 7. 한 개
    # -----------------------------------------------------

    if (
        "한 개" in text
        or "한개" in text
        or "하나" in text
    ):

        return food["unit_g"]


    # -----------------------------------------------------
    # 8. 반 개
    # -----------------------------------------------------

    if (
        "반 개" in text
        or "반개" in text
    ):

        return food["unit_g"] * 0.5


    # -----------------------------------------------------
    # 9. 한 주먹
    # -----------------------------------------------------

    if (
        "한 주먹" in text
        or "한주먹" in text
        or "주먹 만큼" in text
        or "주먹만큼" in text
    ):

        return 100


    # -----------------------------------------------------
    # 10. 주먹의 반
    # -----------------------------------------------------

    if (
        "주먹의 반" in text
        or "주먹 반" in text
        or "주먹의 절반" in text
    ):

        return 50


    # -----------------------------------------------------
    # 11. 한 줌
    # -----------------------------------------------------

    if (
        "한 줌" in text
        or "한줌" in text
    ):

        return 30


    # -----------------------------------------------------
    # 12. 숫자만 입력
    # -----------------------------------------------------

    number_match = re.search(
        r"(\d+(?:\.\d+)?)",
        text
    )

    if number_match:

        return float(
            number_match.group(1)
        )


    # -----------------------------------------------------
    # 13. 해석 실패
    # -----------------------------------------------------

    return None


# =========================================================
# 하루 총 섭취량 계산
# =========================================================

def calculate_total():

    if not st.session_state.intake_list:

        return {
            "칼로리(kcal)": 0,
            "탄수화물(g)": 0,
            "단백질(g)": 0,
            "지방(g)": 0,
            "나트륨(mg)": 0,
            "식이섬유(g)": 0
        }


    df = pd.DataFrame(
        st.session_state.intake_list
    )


    return {

        "칼로리(kcal)": round(
            df["칼로리(kcal)"].sum(),
            1
        ),

        "탄수화물(g)": round(
            df["탄수화물(g)"].sum(),
            1
        ),

        "단백질(g)": round(
            df["단백질(g)"].sum(),
            1
        ),

        "지방(g)": round(
            df["지방(g)"].sum(),
            1
        ),

        "나트륨(mg)": round(
            df["나트륨(mg)"].sum(),
            1
        ),

        "식이섬유(g)": round(
            df["식이섬유(g)"].sum(),
            1
        )
    }


# =========================================================
# 음식 검색
# =========================================================

def search_food(keyword):

    keyword = keyword.strip()

    if not keyword:

        return list(
            FOOD_DB.keys()
        )


    return [

        food
        for food in FOOD_DB.keys()

        if keyword.lower()
        in food.lower()

    ]


# =========================================================
# 일반적인 영양 기준
# =========================================================

def get_general_targets(age):

    if age <= 13:

        return {

            "칼로리": 2000,
            "탄수화물": 300,
            "단백질": 50,
            "지방": 70,
            "나트륨": 2000,
            "식이섬유": 25

        }


    elif age <= 18:

        return {

            "칼로리": 2300,
            "탄수화물": 330,
            "단백질": 55,
            "지방": 75,
            "나트륨": 2000,
            "식이섬유": 25

        }


    else:

        return {

            "칼로리": 2200,
            "탄수화물": 300,
            "단백질": 60,
            "지방": 70,
            "나트륨": 2000,
            "식이섬유": 25

        }


# =========================================================
# 식단 추천 함수
# =========================================================

def recommend_foods(
    preference,
    meal
):

    if preference == "단백질 중심":

        if meal == "아침":

            return [
                "계란",
                "현미밥",
                "우유"
            ]

        elif meal == "점심":

            return [
                "닭가슴살",
                "현미밥",
                "김치"
            ]

        else:

            return [
                "연어",
                "고구마",
                "두부"
            ]


    elif preference == "가볍게 먹기":

        if meal == "아침":

            return [
                "바나나",
                "요거트",
                "계란"
            ]

        elif meal == "점심":

            return [
                "월남쌈",
                "닭가슴살",
                "사과"
            ]

        else:

            return [
                "두부",
                "고구마",
                "요거트"
            ]


    elif preference == "한식":

        if meal == "아침":

            return [
                "흰밥",
                "계란",
                "김치"
            ]

        elif meal == "점심":

            return [
                "현미밥",
                "닭가슴살",
                "김치"
            ]

        else:

            return [
                "흰밥",
                "고등어",
                "두부"
            ]


    else:

        if meal == "아침":

            return [
                "계란",
                "바나나",
                "우유"
            ]

        elif meal == "점심":

            return [
                "닭가슴살",
                "흰밥",
                "김치"
            ]

        else:

            return [
                "연어",
                "고구마",
                "두부"
            ]


# =========================================================
# 메인 화면
# =========================================================

st.title(
    "🥗 식품 영양 성분 분석 & 맞춤형 식단 관리"
)

st.write(
    "음식의 영양정보를 검색하고 실제 섭취량을 입력하여 "
    "하루 영양 섭취량을 분석할 수 있는 프로그램입니다."
)

st.divider()


# =========================================================
# 사이드바
# =========================================================

st.sidebar.title("👤 사용자 정보")


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


st.sidebar.info(
    "입력한 신체 정보는 식단 추천을 위한 참고 정보로 사용됩니다."
)


# =========================================================
# 탭
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🔎 음식 검색",
        "🍽️ 섭취량 분석",
        "📊 하루 영양 분석",
        "🥗 맞춤 식단 만들기"
    ]
)


# =========================================================
# 1. 음식 검색
# =========================================================

with tab1:

    st.header(
        "🔎 음식 영양정보 검색"
    )


    search = st.text_input(
        "음식 이름을 입력하세요.",
        placeholder="예: 닭가슴살, 밥, 계란"
    )


    results = search_food(search)


    if results:

        selected_food = st.selectbox(
            "검색 결과",
            results
        )


        food = FOOD_DB[
            selected_food
        ]


        st.subheader(
            f"🍴 {selected_food}"
        )


        col1, col2, col3, col4 = st.columns(4)


        with col1:

            st.metric(
                "기준 제공량",
                food["serving"]
            )


        with col2:

            st.metric(
                "칼로리",
                f"{food['calories']} kcal"
            )


        with col3:

            st.metric(
                "탄수화물",
                f"{food['carbs']} g"
            )


        with col4:

            st.metric(
                "단백질",
                f"{food['protein']} g"
            )


        col5, col6, col7 = st.columns(3)


        with col5:

            st.metric(
                "지방",
                f"{food['fat']} g"
            )


        with col6:

            st.metric(
                "나트륨",
                f"{food['sodium']} mg"
            )


        with col7:

            st.metric(
                "식이섬유",
                f"{food['fiber']} g"
            )


    else:

        st.warning(
            "검색한 음식이 데이터베이스에 없습니다."
        )


# =========================================================
# 2. 섭취량 분석
# =========================================================

with tab2:

    st.header(
        "🍽️ 실제 섭취량 분석"
    )


    st.write(
        "먹은 음식과 섭취량을 자연스럽게 입력하면 "
        "프로그램이 실제 섭취량을 계산합니다."
    )


    # -----------------------------------------------------
    # 음식 선택
    # -----------------------------------------------------

    food_name = st.selectbox(
        "음식 선택",
        list(FOOD_DB.keys())
    )


    selected = FOOD_DB[
        food_name
    ]


    st.info(
        f"기준 제공량: {selected['serving']} "
        f"| 기준 중량: {selected['unit_g']}g"
    )


    # -----------------------------------------------------
    # 자연어 섭취량
    # -----------------------------------------------------

    amount_text = st.text_input(
        "섭취량을 입력하세요.",
        placeholder="예: 150g / 2개 / 1공기 / 한 주먹"
    )


    st.caption(
        "입력 예시: 150g · 2개 · 1공기 · 반 공기 · "
        "한 주먹 · 주먹의 반 · 한 줌"
    )


    # -----------------------------------------------------
    # 계산
    # -----------------------------------------------------

    if st.button(
        "➕ 섭취 기록 추가",
        use_container_width=True
    ):


        if not amount_text.strip():

            st.warning(
                "섭취량을 입력해주세요."
            )


        else:

            amount = parse_amount(
                amount_text,
                food_name
            )


            if amount is None:

                st.error(
                    "섭취량을 이해하지 못했습니다."
                )

                st.info(
                    "예: 150g, 2개, 1공기, "
                    "반 공기, 한 주먹"
                )


            else:

                result = calculate_nutrition(
                    food_name,
                    amount
                )


                # 사용자가 실제 입력한 표현 저장
                result[
                    "입력한 섭취량"
                ] = amount_text


                st.session_state.intake_list.append(
                    result
                )


                st.success(
                    f"{food_name} "
                    f"{amount_text} → "
                    f"약 {amount:g}g으로 계산했습니다."
                )


                if (
                    "주먹" in amount_text
                    or "줌" in amount_text
                ):

                    st.caption(
                        "※ '한 주먹', '한 줌' 등은 "
                        "사람마다 크기가 다르므로 "
                        "대략적인 양으로 계산됩니다."
                    )


    # -----------------------------------------------------
    # 오늘 먹은 음식
    # -----------------------------------------------------

    st.divider()


    st.subheader(
        "📋 오늘 먹은 음식"
    )


    if st.session_state.intake_list:


        df = pd.DataFrame(
            st.session_state.intake_list
        )


        columns = [

            "음식",
            "입력한 섭취량",
            "섭취량",
            "칼로리(kcal)",
            "탄수화물(g)",
            "단백질(g)",
            "지방(g)",
            "나트륨(mg)",
            "식이섬유(g)"

        ]


        df = df[
            [
                col
                for col in columns
                if col in df.columns
            ]
        ]


        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


        # -------------------------------------------------
        # 현재 총 섭취량
        # -------------------------------------------------

        total = calculate_total()


        st.subheader(
            "📊 현재까지의 총 섭취량"
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "칼로리",
                f"{total['칼로리(kcal)']} kcal"
            )


        with col2:

            st.metric(
                "탄수화물",
                f"{total['탄수화물(g)']} g"
            )


        with col3:

            st.metric(
                "단백질",
                f"{total['단백질(g)']} g"
            )


        col4, col5, col6 = st.columns(3)


        with col4:

            st.metric(
                "지방",
                f"{total['지방(g)']} g"
            )


        with col5:

            st.metric(
                "나트륨",
                f"{total['나트륨(mg)']} mg"
            )


        with col6:

            st.metric(
                "식이섬유",
                f"{total['식이섬유(g)']} g"
            )


        # -------------------------------------------------
        # 기록 삭제
        # -------------------------------------------------

        if st.button(
            "🗑️ 전체 섭취 기록 삭제"
        ):

            st.session_state.intake_list = []

            st.rerun()


    else:

        st.info(
            "아직 입력된 음식이 없습니다."
        )


# =========================================================
# 3. 하루 영양 분석
# =========================================================

with tab3:

    st.header(
        "📊 하루 영양 섭취 분석"
    )


    total = calculate_total()

    targets = get_general_targets(
        age
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "총 칼로리",
            f"{total['칼로리(kcal)']} kcal"
        )


    with col2:

        st.metric(
            "탄수화물",
            f"{total['탄수화물(g)']} g"
        )


    with col3:

        st.metric(
            "단백질",
            f"{total['단백질(g)']} g"
        )


    col4, col5, col6 = st.columns(3)


    with col4:

        st.metric(
            "지방",
            f"{total['지방(g)']} g"
        )


    with col5:

        st.metric(
            "나트륨",
            f"{total['나트륨(mg)']} mg"
        )


    with col6:

        st.metric(
            "식이섬유",
            f"{total['식이섬유(g)']} g"
        )


    st.divider()


    st.subheader(
        "📈 일반적인 영양 기준과 비교"
    )


    comparison = pd.DataFrame(

        {
            "영양소": [
                "칼로리",
                "탄수화물",
                "단백질",
                "지방",
                "나트륨",
                "식이섬유"
            ],

            "현재 섭취량": [

                total["칼로리(kcal)"],
                total["탄수화물(g)"],
                total["단백질(g)"],
                total["지방(g)"],
                total["나트륨(mg)"],
                total["식이섬유(g)"]

            ],

            "참고 기준": [

                targets["칼로리"],
                targets["탄수화물"],
                targets["단백질"],
                targets["지방"],
                targets["나트륨"],
                targets["식이섬유"]

            ]
        }
    )


    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )


    st.bar_chart(
        comparison.set_index(
            "영양소"
        )
    )


    st.caption(
        "※ 위 기준은 프로그램의 일반적인 비교용 값이며 "
        "개인에게 맞는 의료·영양 처방값이 아닙니다."
    )


# =========================================================
# 4. 맞춤 식단 만들기
# =========================================================

with tab4:

    st.header(
        "🥗 맞춤형 식단 만들기"
    )


    st.write(
        "현재 상태와 선호하는 음식 유형을 바탕으로 "
        "여러 날의 식단 예시를 생성합니다."
    )


    mood = st.selectbox(
        "오늘의 상태",
        [
            "평소와 비슷함",
            "피곤함",
            "집중해서 공부하고 싶음",
            "가볍게 먹고 싶음"
        ]
    )


    preference = st.selectbox(
        "먹고 싶은 식단 스타일",
        [
            "균형 잡힌 식단",
            "단백질 중심",
            "가볍게 먹기",
            "한식"
        ]
    )


    days = st.slider(
        "몇 일의 식단을 만들까요?",
        min_value=1,
        max_value=7,
        value=3
    )


    meals = st.multiselect(
        "식단을 만들 식사",
        [
            "아침",
            "점심",
            "저녁"
        ],
        default=[
            "아침",
            "점심",
            "저녁"
        ]
    )


    if st.button(
        "🥗 식단 생성",
        use_container_width=True
    ):


        if not meals:

            st.warning(
                "최소 한 가지 식사를 선택해주세요."
            )


        else:

            st.success(
                f"{days}일 동안의 식단을 생성했습니다."
            )


            for day in range(
                1,
                days + 1
            ):


                st.subheader(
                    f"📅 {day}일차"
                )


                for meal in meals:


                    foods = recommend_foods(
                        preference,
                        meal
                    )


                    st.markdown(
                        f"**{meal}**"
                    )


                    food_text = " · ".join(
                        foods
                    )


                    st.write(
                        food_text
                    )


                    # -------------------------------------------------
                    # 간단한 영양성분 계산
                    # -------------------------------------------------

                    calories = 0

                    protein = 0


                    for food in foods:

                        data = FOOD_DB[
                            food
                        ]


                        calories += (
                            data["calories"]
                        )


                        protein += (
                            data["protein"]
                        )


                    st.caption(
                        f"예상 영양정보: "
                        f"{calories:.0f} kcal · "
                        f"단백질 {protein:.1f}g"
                    )


                st.divider()


# =========================================================
# 푸터
# =========================================================

st.divider()


st.caption(
    "🥗 Food Nutrition & Personalized Meal Planner"
)


st.caption(
    "이 프로그램은 영양정보 확인 및 식단 계획을 위한 "
    "참고용 프로그램입니다."
)
```
