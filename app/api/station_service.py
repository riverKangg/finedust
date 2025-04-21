import os
import json
import requests
import xmltodict
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import unquote

# .env에서 API 키 불러오기
load_dotenv()
API_KEY = unquote(os.getenv("DUST_API_KEY"))
print(API_KEY)

def fetch_station_info(addr="서울", station_name="종로구", num_of_rows=100000):
    url = 'http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getMsrstnList'
    params = {
        'serviceKey': API_KEY,
        'returnType': 'xml',
        'numOfRows': num_of_rows,
        #'pageNo': '1',
        #'addr': "경기도",
        #'stationName': station_name
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"API 호출 실패: {response.status_code}")

    # XML → 딕셔너리로 변환
    data = xmltodict.parse(response.content)
    return data

def save_to_json(data, filename="db/stations.json"):
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    
    # XML 파싱된 dict에서 실제 item 리스트만 뽑기
    try:
        items = data['response']['body']['items']['item']
    except (KeyError, TypeError):
        items = []

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"✅ 측정소 정보 {len(items)}개 저장 완료 → {filename}")

# 테스트 실행용
if __name__ == "__main__":
    result = fetch_station_info()
    save_to_json(result)
