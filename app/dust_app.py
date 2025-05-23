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

valid_data = next((d for d in dust_data if d and d.get("dataTime")), None)
timestamp_str = valid_data.get("dataTime", "알 수 없음") if valid_data else "알 수 없음"

try:
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
    timestamp_str_fmt = timestamp.strftime("%Y년 %m월 %d일 %H시 %M분 기준")
    now = datetime.now()
    delta = now - timestamp
except Exception as e:
    timestamp_str_fmt = f"업데이트 시간: {timestamp_str} (오류: {e})"
     

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

# 지도 만들기
def make_map(pollutant="pm10"):
    m = folium.Map(location=[37.49, 127.026], zoom_start=11, tiles="CartoDB positron")

    for item in dust_data:
        name = item["stationName"]
        flag = item[f"{pollutant}Flag"]
        if flag in BAD_VALUES:
            value = "점검 중"
            emoji = "정보 없음 ❓"
        else:
            value = item[f"{pollutant}Value"]
            emoji = get_level_emoji(value, pollutant)

        # value = item[f"{pollutant}Value"] if flag not in BAD_VALUES else "N/A"
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

            # folium.Marker(
            #     location=coord,
            #     icon=folium.DivIcon(html=f"""<div style="font-size:10px;color:{color};">{name}</div>""")
            # ).add_to(m)

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
st.markdown("**서울 및 주요 지역의 대기질 정보 (PM10 & PM2.5)**")
st.markdown(f"**업데이트 시간:** {timestamp_str_fmt}") 

# 주요 관측소 결과
st.markdown("### 🧭 주요 측정소 요약")

fixed_stations = ["서초구", "대왕판교로(백현동)", "백령도"]
cols = st.columns(len(fixed_stations))

for i, name in enumerate(fixed_stations):
    item = next((d for d in dust_data if d["stationName"] == name), None)
    if not item:
        cols[i].error(f"{name} 데이터 없음")
        continue

    pm10 = item["pm10Value"]
    pm25 = item["pm25Value"]
    flag10 = item["pm10Flag"]
    flag25 = item["pm25Flag"]

    if flag10 in BAD_VALUES:
        pm10 = "점검 중"
        emoji10 = "❓"
    else:
        emoji10 = get_level_emoji(pm10, "pm10")

    if flag25 in BAD_VALUES:
        pm25 = "점검 중"
        emoji25 = "❓"
    else:
        emoji25 = get_level_emoji(pm25, "pm25")

    cols[i].markdown(f"""
    <div style="border:2px solid #ccc; border-radius:10px; padding:10px; text-align:center; background-color:#f9f9f9;">
        <b>{name}</b><br>
        🌫️ PM10: <b>{pm10}</b> {emoji10}<br>
        🌁 PM2.5: <b>{pm25}</b> {emoji25}
    </div>
    """, unsafe_allow_html=True)


# 지도 표시
tab1, tab2 = st.tabs(["PM10 (미세먼지)", "PM2.5 (초미세먼지)"])

with tab1:
    st_folium(make_map("pm10"), width=None, height=200)

with tab2:
    st_folium(make_map("pm25"), width=None, height=200)

# 📊 표 정보
marker_info_list = []
for item in dust_data:
    sido = item["sidoName"]
    name = item["stationName"]
    pm10 = item["pm10Value"]
    pm25 = item["pm25Value"]
    coord = station_coords.get(name)
    if coord:
        marker_info_list.append({
            "시도": sido,
            "측정소": name,
            "PM10": f"{pm10} ({get_level_emoji(pm10, 'pm10')})",
            "PM2.5": f"{pm25} ({get_level_emoji(pm25, 'pm25')})",
            "위도": coord[1],
            "경도": coord[0]
        })

df = pd.DataFrame(marker_info_list)
df = df.drop(columns=["위도", "경도"])

# 상위 고정 측정소 설정
fixed_stations = ["서초구", "대왕판교로(백현동)", "백령도"]
fixed_df = df[df["측정소"].isin(fixed_stations)]
others_df = df[~df["측정소"].isin(fixed_stations)]

# 정렬 후 결합
sorted_df = pd.concat([fixed_df, others_df])
sorted_df = sorted_df.sort_values(by="시도")
sorted_df = sorted_df.reset_index(drop=True)

# 필터링 기능 추가
with st.expander("🔍 측정소 필터링"):
    query = st.text_input("측정소 이름으로 검색")
    if query:
        sorted_df = sorted_df[sorted_df["측정소"].str.contains(query)]

st.markdown("### 📊 측정소별 데이터")
st.dataframe(sorted_df, use_container_width=True)
