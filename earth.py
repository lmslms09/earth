import streamlit as st
import pandas as pd
import joblib
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import base64

# 페이지 설정
st.set_page_config(
    page_title="뽀로로와 함께하는 세계 지진 탐험대", 
    page_icon="🐧", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 이미지 링크 정의
IMG_LOGO = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTurfCwox21Y6XbJJTOMTmFh8_o-WBTUPkv4w&s"
IMG_PORORO = "https://i.pinimg.com/474x/f2/44/2b/f2442b5de34900a1e9bd9aa058f27aed.jpg"
IMG_LOOPY = "https://static.ebs.co.kr/images/ebs/WAS-HOME/portal/upload/img/programinfo/person/per/1242723572507_BOtiBfIuyL.jpg"
IMG_POBEE = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRTAvmhpxHhOX-YZEgYVbFitaGXAS9Fhr86gA&s"
IMG_CRONG = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCKJQlE4yfBkxlYpbX2bIfm0AnLZRyYFjN-Q&s"

# 💡 [추가] 스트림릿 재실행 시 상태를 유지하기 위한 session_state 초기화
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "lat" not in st.session_state:
    st.session_state.lat = 36.0
if "lon" not in st.session_state:
    st.session_state.lon = 127.0

# ==========================================
# [글꼴 및 뽀로로 테마 CSS 설정]
# ==========================================
FONT_PATH = "font.ttf"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: #F0F8FF; }}
    div.stButton > button:first-child {{
        background-color: #FF7F50 !important;
        color: white !important;
        border-radius: 20px !important;
        border: 2px solid #FF4500 !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }}
    [data-testid="stSidebar"] {{ background-color: #1E90FF !important; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] span {{ color: white !important; }}
    
    .pororo-character-circle {{
        display: inline-block;
        background-color: white;
        border-radius: 50%;
        padding: 8px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        border: 2px solid #FFD700;
        margin-bottom: 10px;
    }}
    .pororo-character-circle img {{ border-radius: 50%; object-fit: cover; }}
    .main-logo-container {{
        text-align: center;
        background-color: white;
        padding: 15px;
        border-radius: 30px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        border: 4px solid #1E90FF;
        margin-bottom: 20px;
        display: inline-block;
    }}
    .centered-container {{ display: flex; justify-content: center; align-items: center; flex-direction: column; width: 100%; }}
    .pororo-title {{ color: #1E90FF; font-size: 36px; font-weight: 900; text-align: center; text-shadow: 1px 1px #FFD700; }}
    </style>
    """,
    unsafe_allow_html=True
)

if os.path.exists(FONT_PATH):
    with open(FONT_PATH, "rb") as f: font_data = f.read()
    b64_font = base64.b64encode(font_data).decode()
    st.markdown(f"<style>@font-face {{ font-family: 'CustomFont'; src: url(data:font/ttf;base64,{b64_font}) format('truetype'); }} html, body, [data-testid='stWidgetLabel'], .stMarkdown, h1, h2, h3, h4, h5, h6, p, span, button {{ font-family: 'CustomFont', sans-serif !important; }}</style>", unsafe_allow_html=True)

# ==========================================
# 데이터 로드
# ==========================================
@st.cache_resource
def load_artifacts():
    scaler = joblib.load('earth_scaler.pkl')
    model_4 = joblib.load('earth.pkl')
    return scaler, model_4

scaler, model_4 = load_artifacts()

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('earthquake.csv')
        if 'cluster_4' not in df.columns:
            X_features = df[['영향도', '규모', '진원깊이']]
            X_scaled = scaler.transform(X_features)
            df['cluster_4'] = model_4.predict(X_scaled)
        return df
    except:
        return None

df_new = load_data()

risk_dict = {
    0: '🔥 위험 (크롱이 화났어요!)', 
    1: '😮 주의 (루피가 깜짝 놀랐어요!)', 
    2: '💚 안전 (포비처럼 든든해요!)', 
    3: '😮 주의 (루피가 깜짝 놀랐어요!)'
}
colors = {0: 'red', 1: 'orange', 2: 'green', 3: 'orange'}
character_imgs = {0: IMG_CRONG, 1: IMG_LOOPY, 2: IMG_POBEE, 3: IMG_LOOPY}

# ==========================================
# 사이드바
# ==========================================
with st.sidebar:
    st.markdown(f"<div class='centered-container'><div class='pororo-character-circle'><img src='{IMG_PORORO}' width='120'></div></div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: white;'>대장 뽀로로</p>", unsafe_allow_html=True)
    st.header("🧭 탐험 위치 설정")
    
    # 슬라이더 입력을 변수에 바로 넣지 않고 session_state에 연동시킵니다.
    lat = st.slider("위도 (Latitude)", -90.0, 90.0, st.session_state.lat, 0.1)
    lon = st.slider("경도 (Longitude)", -180.0, 180.0, st.session_state.lon, 0.1)
    
    predict_btn = st.button("🔍 탐험 시작!", use_container_width=True)
    
    # 버튼을 누르면 상태를 True로 고정하고 좌표를 박제합니다.
    if predict_btn:
        st.session_state.analyzed = True
        st.session_state.lat = lat
        st.session_state.lon = lon

# ==========================================
# 메인 화면
# ==========================================
st.markdown(
    f"""
    <div class="centered-container">
        <div class="main-logo-container">
            <img src="{IMG_LOGO}" width="300" alt="뽀로로 로고">
        </div>
        <div class="pororo-title">🌋 세계 지진 탐험대</div>
        <p style="color: #555;">에디와 친구들이 분석하는 우리 동네 안전 지수!</p>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# 💡 [핵심 수정] 버튼 변수 대신 session_state.analyzed 상태 조건문으로 변경
if st.session_state.analyzed:
    # 한 번 저장된 좌표를 고정해서 사용합니다.
    current_lat = st.session_state.lat
    current_lon = st.session_state.lon
    
    if df_new is None:
        st.warning("데이터프레임 로드가 실패하여 분석을 진행할 수 없습니다.")
    else:
        near_df = df_new[
            (df_new['위도'] >= current_lat - 5) & (df_new['위도'] <= current_lat + 5) & 
            (df_new['경도'] >= current_lon - 5) & (df_new['경도'] <= current_lon + 5)
        ]
        
        if near_df.empty:
            st.info("기록이 없는 아주 깨끗한 지역이에요!")
            m = folium.Map(location=[current_lat, current_lon], zoom_start=4)
        else:
            cluster_ratio = near_df['cluster_4'].value_counts(normalize=True)
            main_cluster = cluster_ratio.idxmax()
            
            res_col1, res_col2 = st.columns([1, 2])
            with res_col1:
                st.markdown(f"<div class='pororo-character-circle'><img src='{character_imgs.get(main_cluster)}' width='200'></div>", unsafe_allow_html=True)
            with res_col2:
                st.success(f"### 분석 결과: {risk_dict.get(main_cluster)}")
                st.metric("탐험지 안전 정밀도", f"{cluster_ratio[main_cluster]*100:.1f}%")
            
            m = folium.Map(location=[current_lat, current_lon], zoom_start=5)
            # 샘플링하여 지도에 표시
            for _, row in near_df.head(200).iterrows():
                folium.CircleMarker(location=[row['위도'], row['경도']], radius=4, color=colors.get(int(row['cluster_4']), 'gray'), fill=True).add_to(m)
        
        folium.Marker([current_lat, current_lon], icon=folium.Icon(color='orange', icon='star')).add_to(m)
        
        # returned_objects=[]를 주어 지도를 클릭해도 무의미한 세션 리런이 발생하는 것을 방지합니다.
        st_folium(m, width="100%", height=500, returned_objects=[])

else:
    # 대기 화면 친구들 소개
    st.info("왼쪽 탐험 컨트롤러에서 위치를 정하고 [탐험 시작]을 눌러봐!")
    intro_col1, intro_col2, intro_col3 = st.columns(3)
    with intro_col1:
        st.markdown(f"<div class='centered-container'><div class='pororo-character-circle'><img src='{IMG_POBEE}' width='100'></div><p><b>포비 (안전)</b></p></div>", unsafe_allow_html=True)
    with intro_col2:
        st.markdown(f"<div class='centered-container'><div class='pororo-character-circle'><img src='{IMG_LOOPY}' width='100'></div><p><b>루피 (주의)</b></p></div>", unsafe_allow_html=True)
    with intro_col3:
        st.markdown(f"<div class='centered-container'><div class='pororo-character-circle'><img src='{IMG_CRONG}' width='100'></div><p><b>크롱 (위험)</b></p></div>", unsafe_allow_html=True)