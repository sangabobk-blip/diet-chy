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
