
import streamlit as st
import pandas as pd
from pathlib import Path
from urllib.parse import quote_plus
import random

st.set_page_config(
    page_title="THE DINING TABLE",
    page_icon="G",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "kitchen_home.png"

# -----------------------------
# 페이지 및 세션 상태 초기화
# -----------------------------
VALID_PAGES = {"home", "nutrition", "meal", "farm", "bmi"}

requested_page = st.query_params.get("page", "home")
if requested_page not in VALID_PAGES:
    requested_page = "home"
st.session_state.page = requested_page

if "intake" not in st.session_state:
    st.session_state.intake = []
if "suggestion" not in st.session_state:
    st.session_state.suggestion = ""

def set_page(page):
    if page not in VALID_PAGES:
        page = "home"
    st.session_state.page = page
    st.query_params["page"] = page

def back_home():
    set_page("home")

# -----------------------------
# 디자인: 절제된 프리미엄 타이포그래피
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Noto+Serif+KR:wght@400;500;600;700&family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

:root {
    --bg: #171310;
    --gold: #c8a66b;
    --line: #59452f;
    --text: #eee6da;
}

html, body, [class*="css"], button, input, textarea, select,
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] {
    font-family: 'Noto Sans KR', sans-serif !important;
}

body, p, li, label, input, textarea, select, button,
[data-testid="stWidgetLabel"] {
    letter-spacing: -0.01em;
}


.stApp {
    background: var(--bg);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: rgba(23,19,16,.92);
}

.block-container {
    max-width: 1180px;
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Noto Serif KR', serif !important;
}

/* 브랜드 로고와 영문 장식 문구는 Cormorant Garamond로 통일 */
.brand, .kicker, .sidebar-brand, .sidebar-kicker, .sidebar-section-label,
.english-menu, .english-title {
    font-family: 'Cormorant Garamond', 'Noto Serif KR', serif !important;
}

[data-testid="stSidebar"] * {
    font-family: 'Noto Sans KR', sans-serif !important;
}
[data-testid="stSidebar"] .sidebar-brand,
[data-testid="stSidebar"] .sidebar-kicker,
[data-testid="stSidebar"] .sidebar-section-label {
