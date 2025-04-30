import requests
from sqlalchemy import create_engine, text
import time

# ✅ 替换为你自己的信息
AMAP_KEY = '4194c76cb632b17d74ff6144472ad27d'
MYSQL_URL = 'mysql+pymysql://root:1234@localhost:3306/poi_query_system?charset=utf8mb4'

engine = create_engine(MYSQL_URL)

# ✅ 需要抓取的多个中心点（经度, 纬度）
locations = [
    (116.397470, 39.908823),  # 北京天安门
    (121.4737, 31.2304),      # 上海人民广场
    (114.3054, 30.5928),      # 武汉中心
    (113.2644, 23.1291),      # 广州中心
    (123.429, 41.805)         # 沈阳北站
]

def fetch_and_insert(lat, lng, radius=2000):
    url = "https://restapi.amap.com/v3/place/around"
    params = {
        'key': AMAP_KEY,
        'location': f"{lng},{lat}",
        'radius': radius,
        'output': 'JSON',
        'offset': 20,
        'page': 1,
        'types': ''  # 全部
    }

    res = requests.get(url, params=params)
    pois = res.json().get('pois', [])

    inserted = 0
    with engine.connect() as conn:
        for item in pois:
            if not item.get('location'):
                continue
            lng_str, lat_str = item['location'].split(',')
            lng_f, lat_f = float(lng_str), float(lat_str)
            wkt = f"POINT({lng_f} {lat_f})"
            try:
                wkt = f"POINT({lng_f} {lat_f})"
                conn.execute(text("""
                    INSERT INTO pois (name, category, description, longitude, latitude, rating, tags, location)
                    VALUES (:name, :category, :description, :lng, :lat, 4.0, :tags, ST_GeomFromText(:wkt))
                """), {
                    'name': item.get('name'),
                    'category': item.get('type'),
                    'description': item.get('address', ''),
                    'lat': lat_f,
                    'lng': lng_f,
                    'tags': '["自动抓取"]',
                    'wkt': wkt
                })
                inserted += 1
            except Exception as e:
                print("跳过重复或异常记录：", e)
    print(f"📍 抓取 {lat},{lng} 成功插入 {inserted} 条")
    return inserted

if __name__ == "__main__":
    for lng, lat in locations:
        fetch_and_insert(lat, lng)
        time.sleep(1)  # 避免频率限制
