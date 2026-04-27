import streamlit as st
import FinanceDataReader as fdr
import plotly.graph_objects as go
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import math
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import random
import json
import os
import time

# --- 0. 데이터 지속성 설정 (Persistence Management) ---
SAVE_FILE = "targets_config.json"

def load_settings():
    """저장된 파일에서 종목 설정을 불러옵니다."""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    return None

def save_settings():
    """현재 세션의 종목 설정을 JSON 파일로 영구 저장합니다."""
    settings = {
        "economy_targets": st.session_state.economy_targets,
        "etf_targets": st.session_state.etf_targets,
        "stock_targets": st.session_state.stock_targets
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

# --- 1. 페이지 설정 및 커스텀 테마 (UX/UI) ---
st.set_page_config(page_title="STRATEGIC WAR ROOM V2", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
    .stApp { background-color: #0E1217; color: #E8EDF2; font-family: 'Roboto Mono', monospace; }
    
    .header-text {
        font-family: 'Orbitron', sans-serif; text-align: center; color: #C2A56D;
        text-shadow: 0 0 15px rgba(194, 165, 109, 0.5); letter-spacing: 5px; 
        border-bottom: 2px solid #C2A56D; padding: 25px 0; margin-bottom: 15px; 
        background: rgba(194, 165, 109, 0.05);
    }
    .header-text h1 { font-size: 3.5rem !important; margin: 0; }
    
    .section-container {
        border: 1px solid rgba(194, 165, 109, 0.3); padding: 25px; border-radius: 12px;
        background: rgba(26, 36, 45, 0.4); margin-bottom: 20px;
    }
    .section-title {
        font-family: 'Orbitron', sans-serif; color: #C2A56D; font-size: 1.5rem; 
        margin-bottom: 20px; font-weight: 700; border-left: 6px solid #C2A56D; padding-left: 15px;
    }
    
    .ai-briefing-box {
        border: 1px solid rgba(194, 165, 109, 0.3); background: rgba(194, 165, 109, 0.05);
        padding: 20px; border-radius: 8px; min-height: 150px;
    }
    .ai-market-label { font-family: 'Orbitron'; font-size: 1.2rem; color: #C2A56D; margin-bottom: 10px; font-weight: 700; }
    .ai-content { color: #d1d1d1; font-size: 1.1rem; line-height: 1.7; }
    .ai-status-bull { color: #4DFF88; font-weight: bold; }
    .ai-status-bear { color: #FF6B6B; font-weight: bold; }
    
    .metric-card-custom {
        padding: 22px; border-radius: 10px; margin-bottom: 10px;
        border: 1px solid rgba(232, 237, 242, 0.1); background: rgba(30, 41, 51, 0.8);
        transition: transform 0.2s;
    }
    .metric-card-custom:hover { transform: translateY(-3px); border-color: #C2A56D; }
    
    .news-ticker-container {
        border-top: 1px solid #C2A56D; border-bottom: 1px solid #C2A56D;
        background: #1A242D; padding: 12px 0; overflow: hidden; white-space: nowrap; margin-bottom: 15px;
    }
    .news-ticker-content {
        display: inline-block; padding-left: 100%; animation: ticker 250s linear infinite;
    }
    .news-item-inline { display: inline-block; margin-right: 100px; font-size: 1.3rem; color: #E8EDF2; font-weight: 500; }
    @keyframes ticker { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    
    .news-list-item {
        padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05); color: #ccc; font-size: 1.15rem;
    }
    .news-list-item:hover { color: #C2A56D; background: rgba(255,255,255,0.02); }
    
    .status-bar {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: #C2A56D; color: #121920; font-weight: 800; font-size: 16px;
        padding: 8px 25px; z-index: 1000; text-align: right;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
</style>
<div class="header-text"><h1>STRATEGIC ASSET COMMAND CENTER</h1></div>
""", unsafe_allow_html=True)

# --- 2. 데이터 타겟 관리 (Session State & Persistence) ---
saved_config = load_settings()

if 'economy_targets' not in st.session_state:
    if saved_config:
        st.session_state.economy_targets = saved_config["economy_targets"]
    else:
        st.session_state.economy_targets = {
            "미국 환율": {"ticker": "USD/KRW", "unit": "KRW"},
            "엔 환율": {"ticker": "JPY/KRW", "unit": "KRW"},
            "금 선물": {"ticker": "GC=F", "unit": "USD"},
            "WTI 선물": {"ticker": "CL=F", "unit": "USD"},
            "미 국채 10Y": {"ticker": "^TNX", "unit": "%"}
        }

if 'etf_targets' not in st.session_state:
    if saved_config:
        st.session_state.etf_targets = saved_config["etf_targets"]
    else:
        st.session_state.etf_targets = {
            "🇺🇸 S&P 500": {"ticker": "^GSPC", "unit": "pts"},
            "🇺🇸 NASDAQ": {"ticker": "^IXIC", "unit": "pts"},
            "🇰🇷 KOSPI": {"ticker": "KS11", "unit": "pts"},
            "🇯🇵 Nikkei 225": {"ticker": "^N225", "unit": "pts"}
        }

if 'stock_targets' not in st.session_state:
    if saved_config:
        st.session_state.stock_targets = saved_config["stock_targets"]
    else:
        st.session_state.stock_targets = {
            "NVDA": {"ticker": "NVDA", "unit": "USD"},
            "AVGO": {"ticker": "AVGO", "unit": "USD"},
            "PLTR": {"ticker": "PLTR", "unit": "USD"},
            "GOOG": {"ticker": "GOOGL", "unit": "USD"},
            "AAPL": {"ticker": "AAPL", "unit": "USD"},
            "삼성전자": {"ticker": "005930", "unit": "KRW"},
            "SK하이닉스": {"ticker": "000660", "unit": "KRW"}
        }

all_targets = {**st.session_state.economy_targets, **st.session_state.etf_targets, **st.session_state.stock_targets}

# --- 3. 핵심 데이터 엔진 ---
@st.cache_data(ttl=60)
def fetch_data(code, days=400):
    try:
        df = fdr.DataReader(code).tail(days + 60)
        if df is None or df.empty: return None
        df.columns = [c.lower() for c in df.columns]
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma60'] = df['close'].rolling(window=60).mean()
        return df.tail(days)
    except: return None

@st.cache_data(ttl=300)
def fetch_expanded_news():
    news_items = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    sections = [("시장", "258"), ("국제", "262")]
    try:
        for label, sec_id in sections:
            url = f"https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2={sec_id}"
            resp = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(resp.text, 'html.parser')
            titles = soup.select('.articleSubject a')
            for t in titles:
                text = t.get_text(strip=True)
                if text: news_items.append(f"[{label}] {text}")
        random.shuffle(news_items)
        return news_items[:50]
    except: return ["뉴스 데이터 링크 불안정. 백업 시스템 가동 중..."]

def get_simple_tactical_report(market_name, ticker):
    df = fetch_data(ticker, 10)
    if df is None: return "데이터 스캔 중... 통신 상태를 확인하십시오."
    
    curr = df['close'].iloc[-1]
    prev = df['close'].iloc[-2]
    ma20 = df['ma20'].iloc[-1]
    
    change = ((curr - prev) / prev) * 100
    trend = "상승" if curr > ma20 else "하락"
    status_class = "ai-status-bull" if curr > ma20 else "ai-status-bear"
    
    market_label = "미국 작전구역" if market_name == "US" else "한국 작전구역" if market_name == "KR" else "일본 작전구역"
    
    report = f"""
    <div class="ai-content">
        보고: {market_label} 정밀 분석 완료.<br>
        현시점 지수 {curr:,.2f}pt. MA20 대비 <span class="{status_class}">{trend} 모멘텀</span> 감지.<br>
        일일 변동 {change:+.2f}% 기록 중. 전술적 지지선 및 저항선을 스캔 중입니다.
    </div>
    """
    return report

def get_sentiment(df):
    if df is None or len(df) < 2: return "NEUTRAL", "#C2A56D", 50
    curr = df['close'].iloc[-1]
    ma20 = df['ma20'].iloc[-1]
    ma60 = df['ma60'].iloc[-1]
    prev = df['close'].iloc[-2]
    score = 50
    if curr > ma20: score += 15
    else: score -= 15
    if curr > ma60: score += 10
    if (curr - prev) / prev > 0.01: score += 10
    elif (curr - prev) / prev < -0.01: score -= 10
    score = max(0, min(100, score))
    if score >= 75: return "STRONG BULLISH", "#4DFF88", score
    elif score >= 55: return "BULLISH", "#A2FF86", score
    elif score <= 25: return "STRONG BEARISH", "#FF6B6B", score
    elif score <= 45: return "BEARISH", "#FF9F9F", score
    return "NEUTRAL", "#C2A56D", score

def render_metric_card(name, df, unit):
    if df is None: return
    price = df['close'].iloc[-1]
    prev = df['close'].iloc[-2]
    delta = ((price - prev) / prev) * 100
    color = "#FF6B6B" if delta < 0 else "#4DFF88"
    display_price = price * 100 if name == "엔 환율" else price
    display_unit = "KRW/100¥" if name == "엔 환율" else unit
    p_str = f"{display_price:.2f}" if display_unit in ["USD", "%", "JPY", "pts"] else f"{int(display_price):,}"
    st.markdown(f"""
    <div class="metric-card-custom">
        <div style="font-family: Orbitron; font-size: 1.1rem; color: #C2A56D;">{name}</div>
        <div style="font-size:2.3rem; font-weight:800; color:#E8EDF2; margin: 10px 0;">{p_str}<span style="font-size:1.1rem; color:#888;"> {display_unit}</span></div>
        <div style="color:{color}; font-size:1.4rem; font-weight:700;">{"▼" if delta < 0 else "▲"} {abs(delta):.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

# [상단] 실시간 뉴스 티커
expanded_news = fetch_expanded_news()
if expanded_news:
    html_ticker = '<div class="news-ticker-container"><div class="news-ticker-content">'
    for t in expanded_news: html_ticker += f'<span class="news-item-inline">● {t}</span>'
    st.markdown(html_ticker + '</div></div>', unsafe_allow_html=True)

# [확장] 전체 뉴스 리포트
with st.expander("📂 VIEW FULL NEWS INTEL REPORT"):
    for item in expanded_news:
        st.markdown(f'<div class="news-list-item">{item}</div>', unsafe_allow_html=True)

# [섹션] 3대 시장 전술 브리핑
st.markdown('<div class="section-container"><div class="section-title">TACTICAL INTELLIGENCE BRIEFING</div>', unsafe_allow_html=True)
ai_cols = st.columns(3)
with ai_cols[0]:
    analysis_us = get_simple_tactical_report("US", "^GSPC")
    st.markdown(f'<div class="ai-briefing-box"><div class="ai-market-label">🇺🇸 US_THEATER</div>{analysis_us}</div>', unsafe_allow_html=True)
with ai_cols[1]:
    analysis_kr = get_simple_tactical_report("KR", "KS11")
    st.markdown(f'<div class="ai-briefing-box"><div class="ai-market-label">🇰🇷 KR_THEATER</div>{analysis_kr}</div>', unsafe_allow_html=True)
with ai_cols[2]:
    analysis_jp = get_simple_tactical_report("JP", "^N225")
    st.markdown(f'<div class="ai-briefing-box"><div class="ai-market-label">🇯🇵 JP_THEATER</div>{analysis_jp}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# [섹션] 공포-탐욕 심리 게이지
st.markdown('<div class="section-container"><div class="section-title">PSYCHOLOGICAL WARFARE GAUGE</div>', unsafe_allow_html=True)
c1_gauge, c2_info = st.columns([1, 2])
with c1_gauge:
    sp_data = fetch_data("^GSPC", 5)
    _, _, score = get_sentiment(sp_data)
    angle = 180 - (score / 100 * 180)
    r = 0.85
    x_needle = 0.5 + r * 0.45 * math.cos(math.radians(angle))
    y_needle = 0.15 + r * 0.85 * math.sin(math.radians(angle))
    fig_gauge = go.Figure()
    fig_gauge.add_trace(go.Indicator(
        mode = "gauge+number", value = score, domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {'axis': {'range': [0, 100], 'tickfont': {'size': 20}}, 'bar': {'color': "rgba(0,0,0,0)"}, 'bgcolor': "rgba(0,0,0,0)",
                 'steps': [{'range': [0, 25], 'color': '#FF6B6B'}, {'range': [25, 45], 'color': '#FF9F9F'},
                           {'range': [45, 55], 'color': '#444'}, {'range': [55, 75], 'color': '#A2FF86'},
                           {'range': [75, 100], 'color': '#4DFF88'}]}))
    fig_gauge.add_shape(type="line", x0=0.5, y0=0.15, x1=x_needle, y1=y_needle, line=dict(color="#C2A56D", width=6))
    fig_gauge.add_shape(type="circle", x0=0.47, y0=0.12, x1=0.53, y1=0.18, fillcolor="#C2A56D", line_color="#C2A56D")
    fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "#E8EDF2", 'family': "Orbitron", 'size': 18}, 
                            height=250, margin=dict(l=20, r=20, t=40, b=0))
    st.plotly_chart(fig_gauge, width='stretch')
with c2_info:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<div style='border-left: 5px solid #C2A56D; padding: 20px; background: rgba(194, 165, 109, 0.05); font-size:1.5rem;'>현재 시장 공포-탐욕 지수는 <b>{score}pts</b>입니다. <br>심리적 과열 혹은 위축 상태를 상단 전술 분석과 대조하여 작전 계획을 수립하십시오.</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# [섹션] 종목 관리 (Command Configuration)
with st.expander("🛠️ COMMAND CONFIGURATION (종목 추가 및 삭제)"):
    tab1, tab2 = st.tabs(["자산 배치 (Add)", "자산 제거 (Delete)"])
    with tab1:
        c_add1, c_add2, c_add3, c_add4 = st.columns([2, 2, 1, 1])
        new_name = c_add1.text_input("자산 명칭 (예: 비트코인)")
        new_ticker = c_add2.text_input("티커 심볼 (예: BTC/USD)")
        category = c_add3.selectbox("카테고리", ["Economy", "Index", "Stock"])
        suggested_unit = "pts" if "^" in new_ticker or "KS11" in new_ticker else ("KRW" if new_ticker.isdigit() else "USD")
        new_unit = c_add4.selectbox("단위", ["USD", "KRW", "JPY", "pts", "%"], index=["USD", "KRW", "JPY", "pts", "%"].index(suggested_unit) if suggested_unit in ["USD", "KRW", "pts"] else 0)
        if st.button("새 자산 배치 실행", width='stretch'):
            if new_name and new_ticker:
                asset_data = {"ticker": new_ticker, "unit": new_unit}
                if category == "Economy": st.session_state.economy_targets[new_name] = asset_data
                elif category == "Index": st.session_state.etf_targets[new_name] = asset_data
                else: st.session_state.stock_targets[new_name] = asset_data
                save_settings(); st.rerun()
    with tab2:
        del_target = st.selectbox("제거할 자산 선택", list(all_targets.keys()))
        if st.button("자산 노드 연결 해제", width='stretch'):
            if del_target in st.session_state.economy_targets: del st.session_state.economy_targets[del_target]
            elif del_target in st.session_state.etf_targets: del st.session_state.etf_targets[del_target]
            elif del_target in st.session_state.stock_targets: del st.session_state.stock_targets[del_target]
            save_settings(); st.rerun()

# [섹션] 자산 그룹별 대시보드 표시
def display_target_group(title, target_dict, cols_count=5):
    if not target_dict: return
    st.markdown(f'<div class="section-container"><div class="section-title">{title}</div>', unsafe_allow_html=True)
    cols = st.columns(cols_count)
    for i, (name, data) in enumerate(target_dict.items()):
        with cols[i % cols_count]:
            df = fetch_data(data['ticker'], 5)
            render_metric_card(name, df, data['unit'])
    st.markdown('</div>', unsafe_allow_html=True)

display_target_group("🌐 GLOBAL ECONOMY & FX", st.session_state.economy_targets)
display_target_group("📊 GLOBAL MARKET INDEX", st.session_state.etf_targets)
display_target_group("📡 STRATEGIC STOCKS", st.session_state.stock_targets, 6)

# [섹션] 정밀 궤적 분석 차트
st.markdown('<div class="section-container"><div class="section-title">TACTICAL TRAJECTORY ANALYSIS</div>', unsafe_allow_html=True)
cc1, cc2, cc3 = st.columns([1.5, 2, 1.5])
with cc1: sel_target = st.selectbox("노드 선택", list(all_targets.keys()), label_visibility="collapsed")
with cc2: date_range = st.select_slider("분석 범위 (일 단위)", options=[7, 14, 30, 60, 90, 180, 365], value=30, label_visibility="collapsed")
with cc3: 
    target_info = all_targets[sel_target]
    target_df = fetch_data(target_info['ticker'], date_range)
    if target_df is not None:
        t_sent, t_col, _ = get_sentiment(target_df)
        st.markdown(f"<div style='text-align:right; font-family:Orbitron; font-weight:800; color:{t_col}; font-size:1.5rem;'>상태: {t_sent}</div>", unsafe_allow_html=True)

if target_df is not None:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=target_df.index, y=target_df['close'], name="현재가", line=dict(color='#E8EDF2', width=3)))
    fig.add_trace(go.Scatter(x=target_df.index, y=target_df['ma20'], name="MA20", line=dict(color='#C2A56D', width=1.5, dash='dot')))
    fig.add_trace(go.Scatter(x=target_df.index, y=target_df['ma60'], name="MA60", line=dict(color='#4DFF88', width=1.5, dash='dot')))
    y_min, y_max = target_df['close'].min() * 0.99, target_df['close'].max() * 1.01
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      height=480, margin=dict(l=0, r=0, t=20, b=0), xaxis=dict(showgrid=False, tickfont=dict(size=14)),
                      yaxis=dict(side="right", showgrid=True, gridcolor="rgba(255,255,255,0.05)", range=[y_min, y_max], tickfont=dict(size=14)))
    st.plotly_chart(fig, width='stretch')
st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div class="status-bar">COMMAND_CENTER_ACTIVE // SYSTEM_STABILIZED // {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>', unsafe_allow_html=True)
