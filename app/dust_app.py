import os
import streamlit as st
import folium
from streamlit_folium import st_folium
import json

# 측정소와 미세먼지 정보가 담긴 JSON 파일 로드
file_path = os.path.join(os.path.dirname(__file__), 'db', 'realtime_dust.json')
with open(file_path, 'r', encoding='utf-8') as f:
    dust_data = json.load(f)

# 측정소 좌표 정보 로드
station_path = os.path.join(os.path.dirname(__file__), 'db', 'stations.json')
with open(station_path, encoding="utf-8") as f:
    station_data = json.load(f)

# 지도 초기화 (중심: 강남)
m = folium.Map(location=[37.49, 127.026], zoom_start=13, tiles="CartoDB positron")

BAD_VALUES = ["점검및교정", "장비점검", "자료이상", "통신장애"]

def get_color(pm10_value):
    value = int(pm10_value)
    if value <= 30:
        return "blue"
    elif value <= 50:
        return "green"
    elif value <= 100:
        return "yellow"
    else:
        return "red"

# station_name → (lat, lng) dict 만들기
station_coords = {
    s["stationName"]: (float(s["dmX"]), float(s["dmY"]))
    for s in station_data
    if s["dmX"] and s["dmY"]
}

# 마커 정보를 리스트로 저장
marker_info_list = []

# 마커 추가
for item in dust_data:
    name = item["stationName"]
    pm10_flag = item["pm10Flag"]
    pm10 = item["pm10Value"] if pm10_flag not in BAD_VALUES else "ERROR"
    pm25 = item["pm25Value"]
    coord = station_coords.get(name)

    if coord and str(pm10).isdigit():
        color = get_color(pm10)
        popup = f"{name}<br>PM10: {pm10}<br>PM2.5: {pm25}"
        folium.CircleMarker(
            location=coord,
            radius=7,
            color=color,
            fill=True,
            fill_opacity=0.8,
            popup=popup
        ).add_to(m)
        # 리스트에 정보 저장
        marker_info_list.append({
            "측정소": name,
            "PM10": pm10,
            "PM2.5": pm25,
            "위도": coord[1],
            "경도": coord[0],
            "상태": pm10_flag
        })

# Streamlit UI
st.title("실시간 미세먼지 지도")
st.subheader("서울 및 주요 지역의 PM10/PM2.5 상황")

# 지도 표시
st_data = st_folium(m, width=725)

st.write("총 측정소 좌표 수:", len(station_coords))

# 마커 정보 출력
st.markdown("### 측정소별 미세먼지 정보")
for info in marker_info_list:
    st.markdown(f"**{info['측정소']}** - PM10: {info['PM10']} / PM2.5: {info['PM2.5']}")

# 또는 표로 한 번에 출력하고 싶다면 아래 코드 사용:
st.dataframe(marker_info_list)
