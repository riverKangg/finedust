import folium
import json

BAD_VALUES = ["점검및교정", "장비점검", "자료이상", "통신장애"]

# 💨 등급별 색상표 (PM10 기준)
def get_color(pm10_value):
    value = int(pm10_value)
    if value <= 30:
        return "blue"
    elif value <= 50:
        return "green"
    elif value <= 100:
        return "yello"
    else:
        return "red"

# 1. 미세먼지 데이터 로드
with open("db/realtime_dust.json", encoding="utf-8") as f:
    dust_data = json.load(f)

# 2. 측정소 좌표 정보 로드
with open("db/stations.json", encoding="utf-8") as f:
    station_data = json.load(f)

# station_name → (lat, lng) dict 만들기
station_coords = {
    s["stationName"]: (float(s["dmY"]), float(s["dmX"]))
    for s in station_data
    if s["dmX"] and s["dmY"]
}

# 3. 지도 초기화 (중심: 서울)
m = folium.Map(location=[37.5665, 126.9780], 
               zoom_start=7,
               tiles="CartoDB positron"
               )

# 4. 마커 추가
for item in dust_data:
    name = item["stationName"]
    pm10_flag = item["pm10Flag"]
    pm10 = item["pm10Value"] if pm10_flag not in BAD_VALUES else "ERROR"
    print(pm10_flag, pm10)
    pm25 = item["pm25Value"]
    coord = station_coords.get(name)
    print(coord)

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


# 5. 저장
m.save("dust_map.html")
print("✅ 지도 저장 완료: dust_map.html")
