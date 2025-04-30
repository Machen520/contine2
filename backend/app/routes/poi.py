# app/routes/poi.py
from flask import Blueprint, request, jsonify
from app.services.recommend import recommend_poi
from app.models import POI
from app.extensions import db
import requests
from flask import current_app
from app.extensions import cache
from sqlalchemy import text

from backend.app.services.recommend import haversine

poi_bp = Blueprint('poi', __name__)


@poi_bp.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    user_id = data.get('user_id')
    lat = data.get('latitude')
    lng = data.get('longitude')
    radius = data.get('radius', 5000)  # 默认半径5km

    if not all([user_id, lat, lng]):
        return jsonify({'code': 400, 'msg': '缺少参数'})

    # SQL查询POI
    sql = """
    SELECT id, name, category, description, latitude, longitude, rating
    FROM pois
    WHERE ST_Distance_Sphere(point(longitude, latitude), point(:lng, :lat)) <= :radius
    """

    result = db.session.execute(text(sql), {'lng': lng, 'lat': lat, 'radius': radius}).fetchall()

    pois = []
    for row in result:
        poi_lat, poi_lng = float(row[4]), float(row[5])
        distance = haversine(lat, lng, poi_lat, poi_lng)

        # 处理category（兼容高德和OSM）
        raw_category = row[2] or "未知类别"
        if ';' in raw_category:
            category = raw_category.split(';')[0]  # 取第一级
        else:
            category = raw_category

        pois.append({
            'id': row[0],
            'name': row[1],
            'category': category,   # ✅ 用处理后的单一分类
            'description': row[3] or '',
            'lat': poi_lat,
            'lng': poi_lng,
            'rating': float(row[6] or 4.0),
            'distance': round(distance, 2),
            'reason': '距离推荐'
        })

    # 按距离排序
    pois.sort(key=lambda x: x['distance'])

    return jsonify({'code': 200, 'data': pois})




@poi_bp.route('/categories', methods=['GET'])
def get_categories():
    from app.models import POI
    try:
        categories = db.session.query(POI.category).distinct().all()
        cleaned = set()

        for row in categories:
            if not row[0]:
                continue
            cat = row[0].split(';')[0]  # ✅ 只取第一级，如“生活服务”
            cleaned.add(cat.strip())

        return jsonify({'code': 200, 'data': ['全部'] + sorted(cleaned)})
    except Exception as e:
        return jsonify({'code': 500, 'error': str(e)})


@poi_bp.route('/fetch', methods=['POST'])
def fetch_pois():
    print('fetch方法调用')
    data = request.get_json()
    lat = data.get('lat')
    lng = data.get('lng')
    radius = data.get('radius', 1000)

    key = current_app.config.get("AMAP_REST_KEY")
    url = "https://restapi.amap.com/v3/place/around"
    params = {
        'key': key,
        'location': f"{lng},{lat}",
        'radius': radius,
        'output': 'JSON',
        'offset': 5,
        'page': 1,
        'types': ''
    }

    res = requests.get(url, params=params)
    pois = res.json().get('pois', [])

    from sqlalchemy import text
    inserted = 0
    for item in pois:
        if not item.get('location'):
            continue
        lng, lat = map(float, item['location'].split(','))
        location_wkt = f"POINT({lng} {lat})"
        db.session.execute(
            text("""
                INSERT INTO pois (name, category, description, latitude, longitude, rating, tags, location)
                VALUES (:name, :category, :description, :latitude, :longitude, :rating, :tags, ST_GeomFromText(:location, 4326))
            """),
            {
                'name': item.get('name'),
                'category': item.get('type'),
                'description': item.get('address', ''),
                'latitude': lat,
                'longitude': lng,
                'rating': 4.0,
                'tags': '["自动抓取"]',
                'location': location_wkt
            }
        )
        inserted += 1

    db.session.commit()
    return jsonify({'code': 200, 'msg': f'成功获取并插入 {inserted} 条 POI'})


@poi_bp.route('/rate', methods=['POST'])
def rate_poi():
    data = request.get_json()
    poi_id = data.get('poi_id')
    new_rating = data.get('rating')

    if not all([poi_id, new_rating]):
        return jsonify({'code': 400, 'msg': '缺少参数'})

    poi = POI.query.get(poi_id)
    if not poi:
        return jsonify({'code': 404, 'msg': 'POI不存在'})

    try:
        # 动态平滑更新平均分
        poi.rating = (poi.rating * poi.rating_count + new_rating) / (poi.rating_count + 1)
        poi.rating = round(poi.rating, 2)
        poi.rating_count += 1

        db.session.commit()
        return jsonify({'code': 200, 'msg': '评分成功', 'new_rating': poi.rating})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': str(e)})


@poi_bp.route('/comment', methods=['POST'])
def add_comment():
    data = request.get_json()
    user_id = data.get('user_id')
    poi_id = data.get('poi_id')
    content = data.get('content')

    if not all([user_id, poi_id, content]):
        return jsonify({'code': 400, 'msg': '缺少参数'})

    try:
        db.session.execute(text("""
            INSERT INTO poi_comments (user_id, poi_id, content)
            VALUES (:user_id, :poi_id, :content)
        """), {
            'user_id': user_id,
            'poi_id': poi_id,
            'content': content
        })
        db.session.commit()
        return jsonify({'code': 200, 'msg': '评论成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': str(e)})


@poi_bp.route('/comments', methods=['GET'])
def get_comments():
    poi_id = request.args.get('poi_id')
    if not poi_id:
        return jsonify({'code': 400, 'msg': '缺少poi_id'})

    result = db.session.execute(text("""
        SELECT user_id, content, created_at
        FROM poi_comments
        WHERE poi_id = :poi_id
        ORDER BY created_at DESC
    """), {'poi_id': poi_id}).fetchall()

    comments = [{
        'user_id': row[0],
        'content': row[1],
        'created_at': row[2].strftime('%Y-%m-%d %H:%M:%S')
    } for row in result]

    return jsonify({'code': 200, 'data': comments})

