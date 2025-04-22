import os
import streamlit as st
import folium
from streamlit_folium import st_folium
import json
from datetime import datetime
import pandas as pd

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
    timestamp_str_fmt = timestamp.strftime("%Y년 %m월 %d일 %H시 %M분 기준")
    now = datetime.now()
    delta = now - timestamp
    freshness_note = f"⏱️ 업데이트된 지 {int(delta.total_seconds()//60)}분 경과"
except:
    timestamp_str_fmt = f"업데이트 시간: {timestamp_str}"
    freshness_note = "⚠️ 시간 정보 파싱 실패"

# 색상 기준
BAD_VALUES = ["점검및교정", "장비점검", "자료이상", "통신장애"]

def get_color(value, pollutant):
    try:
        value = int(value)
        if pollutant == "pm10":
            if value <= 30: return "blue"
            elif value <= 50: return "green"
            elif value <= 100: return "orange"
            else: return "red"
        elif pollutant == "pm25":
            if value <= 15: return "blue"
            elif value <= 25: return "green"
            elif value <= 50: return "orange"
            else: return "red"
    except:
        return "gray"

def get_level_emoji(value, pollutant):
    try:
        value = int(value)
        if pollutant == "pm10":
            if value <= 30: return "좋음 😊"
            elif value <= 50: return "보통 🙂"
            elif value <= 100: return "나쁨 😷"
            else: return "매우 나쁨 🤢"
        elif pollutant == "pm25":
            if value <= 15: return "좋음 😊"
            elif value <= 25: return "보통 🙂"
            elif value <= 50: return "나쁨 😷"
            else: return "매우 나쁨 🤢"
    except:
        return "정보 없음 ❓"

# 좌표 사전
station_coords = {
    s["stationName"]: (float(s["dmX"]), float(s["dmY"]))
    for s in station_data
    if s["dmX"] and s["dmY"]
}

# 지역 정보 사전
station_region = {
    s["stationName"]: s.get("addr", "").split()[0]
    for s in station_data
}

# 지도 만들기
def make_map(pollutant="pm10", region_filter=None):
    m = folium.Map(location=[37.49, 127.026], zoom_start=11, tiles="CartoDB positron")

    for item in dust_data:
        name = item["stationName"]
        region = station_region.get(name, "")
        if region_filter and region != region_filter:
            continue

        flag = item[f"{pollutant}Flag"]
        value = item[f"{pollutant}Value"] if flag not in BAD_VALUES else "N/A"
        coord = station_coords.get(name)

        if coord and str(value).isdigit():
            color = get_color(value, pollutant)
            emoji = get_level_emoji(value, pollutant)
            popup = f"<b>{name}</b><br>{pollutant.upper()}: {value} ({emoji})"
            folium.CircleMarker(
                location=coord,
                radius=7,
                color=color,
                fill=True,
                fill_opacity=0.8,
                popup=popup
            ).add_to(m)

    # 컬러 범례
    legend_html = '''
     <div style="position: fixed; bottom: 50px; left: 50px; width: 160px; height: 130px;
                 background-color: white; z-index:9999; font-size:14px;
                 border:2px solid gray; padding:10px;">
     <b>PM 등급 기준</b><br>
     <i style="color:blue">●</i> 좋음<br>
     <i style="color:green">●</i> 보통<br>
     <i style="color:orange">●</i> 나쁨<br>
     <i style="color:red">●</i> 매우 나쁨<br>
     <i style="color:gray">●</i> 정보 없음
     </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    return m

# 📍 Streamlit 화면
st.title("🌫️ 실시간 미세먼지 지도")
st.markdown(f"**업데이트 시간:** {timestamp_str_fmt}  \n{freshness_note}")
st.markdown("**서울 및 수도권 지역의 대기질 정보 (PM10 & PM2.5)**")

# 📊 표 정보 생성
marker_info_list = []
for item in dust_data:
    name = item["stationName"]
    pm10 = item["pm10Value"]
    pm25 = item["pm25Value"]
    coord = station_coords.get(name)
    region = station_region.get(name, "")
    if coord:
        marker_info_list.append({
            "지역": region,
            "측정소": name,
            "PM10": f"{pm10} ({get_level_emoji(pm10, 'pm10')})",
            "PM2.5": f"{pm25} ({get_level_emoji(pm25, 'pm25')})",
            "위도": coord[1],
            "경도": coord[0]
        })

df = pd.DataFrame(marker_info_list)

# 고정 측정소 + 지역별 분류
fixed_stations = ["서초구", "대왕판교로(백현동)", "백령도"]
fixed_df = df[df["측정소"].isin(fixed_stations)]
regions = sorted(df["지역"].dropna().unique())

region_tabs = st.tabs(["전체"] + regions)

for i, tab in enumerate(region_tabs):
    with tab:
        if i == 0:
            region_df = df
            st.markdown("### 🗺️ 전체 지역 지도")
            st_folium(make_map("pm10"), width=725)
        else:
            region = regions[i - 1]
            region_df = df[df["지역"] == region]
            st.markdown(f"### 🗺️ {region} 지역 지도")
            st_folium(make_map("pm10", region_filter=region), width=725)

        # 상단 고정 후 정렬
        df_display = pd.concat([
            fixed_df[fixed_df["지역"] == region] if i > 0 else fixed_df,
            region_df[~region_df["측정소"].isin(fixed_stations)]
        ])
        st.markdown("### 📊 측정소별 데이터")
        st.dataframe(df_display.reset_index(drop=True), use_container_width=True)
