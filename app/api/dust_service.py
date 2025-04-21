import os
import requests
import xmltodict
from dotenv import load_dotenv
from urllib.parse import unquote

# .env에서 API 키 불러오기
load_dotenv()
API_KEY = unquote(os.getenv("DUST_API_KEY"))

def fetch_realtime_dust(sido_name="서울", num_of_rows=1000000):
    url = 'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty'
    params = {
        'serviceKey': API_KEY,
        'returnType': 'xml',
        'numOfRows': num_of_rows,
        'pageNo': '1',
        'sidoName': sido_name,
        'ver': '1.0'
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        raise Exception(f"API 호출 실패: {response.status_code}")

    data = xmltodict.parse(response.content)

    try:
        items = data['response']['body']['items']['item']
        if isinstance(items, dict):
            return [items]
        return items
    except (KeyError, TypeError):
        return []

# 테스트 실행용
if __name__ == "__main__":
    from pprint import pprint
    dust_data = fetch_realtime_dust("전국")
    pprint(len(dust_data))
