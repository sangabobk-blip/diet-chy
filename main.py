import streamlit as st
from urllib.parse import quote_plus
from pathlib import Path
import random

st.set_page_config(page_title="그린테이블 | THE DINING TABLE", page_icon="🌿", layout="wide")

# ---------------------------------------------------------
# 디자인: 다크 월넛 브라운 + 차콜 블랙 + 소량의 샴페인 골드
# 한글 Noto Serif KR / 영문 Cormorant Garamond
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Noto+Serif+KR:wght@400;500;600;700&display=swap');

:root {
    --bg: #171310;
    --panel: #211b17;
    --panel-soft: #29211b;
    --text: #eee7dc;
    --muted: #b8aa98;
    --line: #4a392b;
    --gold: #b99a65;
    --gold-soft: #8f7449;
    --cream: #e7dccb;
    --green: #a5ad8b;
}
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    font-family: 'Noto Serif KR', serif;
}
.stApp {
    background:
      radial-gradient(ellipse at 50% 0%, rgba(105,75,47,.18), transparent 48%),
      linear-gradient(145deg, #171310 0%, #211912 48%, #12100e 100%);
    color: var(--text);
}
[data-testid="stHeader"] { background: rgba(23,19,16,.88); }
[data-testid="stToolbar"] { right: 1rem; }
.block-container { max-width: 1220px; padding-top: 1.6rem; padding-bottom: 3rem; }
h1, h2, h3, h4 {
    font-family: 'Noto Serif KR', serif !important;
    color: var(--cream) !important;
    letter-spacing: .015em;
    font-weight: 500 !important;
}
p, li, label, .stMarkdown, .stCaption, [data-testid="stWidgetLabel"] {
    color: var(--text);
}
p { line-height: 1.8; }
a { color: var(--gold) !important; text-decoration-color: rgba(185,154,101,.55) !important; }
a:hover { color: #dfc28e !important; }
.gt-masthead {
    border-bottom: 1px solid var(--line);
    padding: 0 0 1.1rem 0;
    margin-bottom: 1.2rem;
}
.gt-brand {
    font-family: 'Noto Serif KR', serif;
    font-size: clamp(1.8rem, 4vw, 2.6rem);
    letter-spacing: .07em;
    color: #f1e5d3;
    line-height: 1.25;
}
.gt-english {
    font-family: 'Cormorant Garamond', serif;
    color: var(--gold);
    font-size: 1rem;
    letter-spacing: .26em;
    text-transform: uppercase;
}
.gt-subtitle { color: var(--muted); font-size: .96rem; margin-top: .55rem; }
.gt-eyebrow {
    font-family: 'Cormorant Garamond', serif;
    color: var(--gold);
    letter-spacing: .22em;
    font-size: .95rem;
    text-transform: uppercase;
}
.gt-panel {
    background: linear-gradient(145deg, rgba(43,34,27,.96), rgba(29,24,20,.98));
    border: 1px solid var(--line);
    border-radius: 5px;
    padding: 1.15rem 1.25rem;
    margin: .5rem 0 1rem 0;
}
.gt-rule { border: 0; border-top: 1px solid var(--line); margin: 1.3rem 0; }
.gt-muted { color: var(--muted); font-size: .91rem; }
div.stButton > button {
    min-height: 2.9rem;
    border: 1px solid #604a35;
    border-radius: 3px;
    background: #2a211a;
    color: #eee2d0;
    font-family: 'Noto Serif KR', serif;
    font-weight: 500;
    transition: all .15s ease-in-out;
