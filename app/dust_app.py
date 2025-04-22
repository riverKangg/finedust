import os
import streamlit as st
import folium
from streamlit_folium import st_folium
import json
from datetime import datetime

# 파일 경로
BASE_DIR = os.path.dirname(__file__)
dust_path = os.path.join(BASE_DIR, 'db', 'realtime_dust.json')
station_path = os.path.join(BASE_DIR, 'db', 'stations.json')

# JSON 로드
with open(dust_path, 'r', encoding='utf-8') as f:
    dust_data = json.load(f)

with open(station_path, encoding="utf-8") as f:
    station_data = json.load(f)

# timestamp 처리
timestamp_str = dust_data[0].get("dataTime", "알 수 없음")
try:
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
    timestamp = timestamp.strftime("%Y년 %m월 %d일 %H시 %M분 기준")
except:
    timestamp = f"업데이트 시간: {timestamp_str}"

# 색상 기준
BAD_VALUES = ["점검및교정", "장비점검", "자료이상", "통신장애"]

def get_color(value, pollutant):
    try:
        value = int(value)
        if pollutant == "pm10":
            if value <= 30:
                return "blue"
            elif value <= 50:
                return "green"
            elif value <= 100:
                return "orange"
            else:
                return "red"
        elif pollutant == "pm25":
            if value <= 15:
                return "blue"
            elif value <= 25:
                return "green"
            elif value <= 50:
                return "orange"
            else:
                return "red"
    except:
        return "gray"

# 좌표 사전
station_coords = {
    s["stationName"]: (float(s["dmX"]), float(s["dmY"]))
    for s in station_data
    if s["dmX"] and s["dmY"]
}

# 지도 만들기
def make_map(pollutant="pm10"):
    m = folium.Map(location=[37.49, 127.026], zoom_start=11, tiles="CartoDB positron")
    for item in dust_data:
        name = item["stationName"]
        flag = item[f"{pollutant}Flag"]
        value = item[f"{pollutant}Value"] if flag not in BAD_VALUES else "N/A"
        coord = station_coords.get(name)

        if coord and str(value).isdigit():
            color = get_color(value, pollutant)
            popup = f"{name}<br>{pollutant.upper()}: {value}"
            folium.CircleMarker(
                location=coord,
                radius=7,
                color=color,
                fill=True,
                fill_opacity=0.8,
                popup=popup
            ).add_to(m)
    return m

# 📍 Streamlit 화면
st.title("🌫️ 실시간 미세먼지 지도")
st.markdown(f"**업데이트 시간:** {timestamp}")
st.markdown("**서울 및 주요 지역의 대기질 정보 (PM10 & PM2.5)**")

tab1, tab2 = st.tabs(["PM10 (미세먼지)", "PM2.5 (초미세먼지)"])

with tab1:
    st_folium(make_map("pm10"), width=725)

with tab2:
    st_folium(make_map("pm25"), width=725)

# 표 정보
marker_info_list = []
for item in dust_data:
    name = item["stationName"]
    pm10 = item["pm10Value"]
    pm25 = item["pm25Value"]
    coord = station_coords.get(name)
    if coord:
        marker_info_list.append({
            "측정소": name,
            "PM10": pm10,
            "PM2.5": pm25,
            "위도": coord[1],
            "경도": coord[0]
        })

st.markdown("### 📊 측정소별 데이터")
st.dataframe(marker_info_list)
