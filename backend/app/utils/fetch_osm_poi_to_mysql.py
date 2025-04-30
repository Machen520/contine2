import requests
import json
import time
import random
from sqlalchemy import create_engine, text

# ✅ MySQL连接配置
MYSQL_URL = 'mysql+pymysql://root:123456@localhost:3306/poi_query_system?charset=utf8mb4'
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# ✅ 分类映射（英文->中文）
CATEGORY_MAPPING = {
    "restaurant": "餐馆",
    "cafe": "咖啡厅",
    "supermarket": "超市",
    "mall": "商场",
    "park": "公园",
    "museum": "博物馆",
    "cinema": "电影院",
    "hospital": "医院",
    "clinic": "诊所",
    "school": "学校",
    "university": "大学",
    "bank": "银行",
    "bus_station": "公交车站",
    "hotel": "酒店"
}

# 抓取位置的粗略边界框(经纬度范围)
LIAONING_BOUNDS = {
    "min_lat": 34.05,
    "max_lat": 35.10,
    "min_lon": 104.35,
    "max_lon": 106.44
}

# ✅ 网格划分大小 (每格大约10km)
GRID_SIZE_LAT = 0.1  # 纬度每0.1度 ≈ 11km
GRID_SIZE_LON = 0.1  # 经度每0.1度 ≈ 9km

# Overpass请求超时时间
OVERPASS_TIMEOUT = 60

# 创建MySQL连接
engine = create_engine(MYSQL_URL)

# 构建Overpass查询
def build_query(min_lat, min_lon, max_lat, max_lon):
    query = "[out:json][timeout:{timeout}];(".format(timeout=OVERPASS_TIMEOUT)
    for key_value in CATEGORY_MAPPING.keys():
        if key_value in ["supermarket", "mall"]:
            query += f'node["shop"="{key_value}"]({min_lat},{min_lon},{max_lat},{max_lon});'
            query += f'way["shop"="{key_value}"]({min_lat},{min_lon},{max_lat},{max_lon});'
        elif key_value in ["hotel", "museum"]:
            query += f'node["tourism"="{key_value}"]({min_lat},{min_lon},{max_lat},{max_lon});'
            query += f'way["tourism"="{key_value}"]({min_lat},{min_lon},{max_lat},{max_lon});'
        elif key_value in ["park"]:
            query += f'node["leisure"="{key_value}"]({min_lat},{min_lon},{max_lat},{max_lon});'
            query += f'way["leisure"="{key_value}"]({min_lat},{min_lon},{max_lat},{max_lon});'
        else:
            query += f'node["amenity"="{key_value}"]({min_lat},{min_lon},{max_lat},{max_lon});'
            query += f'way["amenity"="{key_value}"]({min_lat},{min_lon},{max_lat},{max_lon});'
    query += ");out center;"
    return query

# 发送请求，自动重试
def fetch_poi_data(min_lat, min_lon, max_lat, max_lon, retries=3):
    query = build_query(min_lat, min_lon, max_lat, max_lon)
    for attempt in range(retries):
        try:
            response = requests.post(OVERPASS_URL, data={"data": query}, timeout=OVERPASS_TIMEOUT+10)
            response.raise_for_status()
            data = response.json()
            return data.get('elements', [])
        except Exception as e:
            print(f"请求失败，尝试第{attempt+1}次重试...错误：{e}")
            time.sleep(2 + attempt * 2)
    print("多次请求失败，跳过此网格。")
    return []

# 插入到MySQL
def insert_pois(elements):
    inserted = 0
    skipped = 0
    seen = set()

    with engine.begin() as conn:
        for el in elements:
            tags = el.get('tags', {})
            name = tags.get('name')
            if not name:
                skipped += 1
                continue

            lat = el.get('lat') or el.get('center', {}).get('lat')
            lon = el.get('lon') or el.get('center', {}).get('lon')
            if lat is None or lon is None:
                skipped += 1
                continue

            unique_key = f"{name}_{round(lat,6)}_{round(lon,6)}"
            if unique_key in seen:
                skipped += 1
                continue
            seen.add(unique_key)

            description = tags.get('description', '')
            tags_json = json.dumps(tags, ensure_ascii=False)

            # 分类映射
            category = "其他"
            for key in ["amenity", "shop", "tourism", "leisure"]:
                if key in tags and tags[key] in CATEGORY_MAPPING:
                    category = CATEGORY_MAPPING[tags[key]]
                    break

            location_wkt = f"POINT({lon} {lat})"

            try:
                conn.execute(text("""
                    INSERT INTO pois (name, category, description, latitude, longitude, rating, tags, location)
                    VALUES (:name, :category, :description, :latitude, :longitude, 4.0, :tags, ST_SRID(ST_GeomFromText(:location), 4326))
                """), {
                    'name': name,
                    'category': category,
                    'description': description,
                    'latitude': lat,
                    'longitude': lon,
                    'tags': tags_json,
                    'location': location_wkt
                })
                inserted += 1
            except Exception as e:
                print(f"跳过 {name} 错误: {e}")
                skipped += 1

    print(f"✅ 插入完成: {inserted} 条，跳过: {skipped} 条。")

# 主流程
def main():
    total_inserted = 0
    total_skipped = 0

    min_lat = LIAONING_BOUNDS["min_lat"]
    max_lat = LIAONING_BOUNDS["max_lat"]
    min_lon = LIAONING_BOUNDS["min_lon"]
    max_lon = LIAONING_BOUNDS["max_lon"]

    lat_steps = int((max_lat - min_lat) / GRID_SIZE_LAT)
    lon_steps = int((max_lon - min_lon) / GRID_SIZE_LON)

    for i in range(lat_steps):
        for j in range(lon_steps):
            cell_min_lat = min_lat + i * GRID_SIZE_LAT
            cell_max_lat = cell_min_lat + GRID_SIZE_LAT
            cell_min_lon = min_lon + j * GRID_SIZE_LON
            cell_max_lon = cell_min_lon + GRID_SIZE_LON

            print(f"🚀 正在抓取格子：({cell_min_lat},{cell_min_lon}) ~ ({cell_max_lat},{cell_max_lon})")
            elements = fetch_poi_data(cell_min_lat, cell_min_lon, cell_max_lat, cell_max_lon)
            print(f"🌟 抓取到 {len(elements)} 条，开始插入...")
            insert_pois(elements)
            time.sleep(random.uniform(0.5, 1.5))  # 防止过快被限制

    print("全部POI网格扫描抓取完毕！")

if __name__ == "__main__":
    main()
