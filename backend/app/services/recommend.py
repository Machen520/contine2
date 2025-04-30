import math
import json
from collections import Counter
from app.models import POI, User, UserPOIHistory
from app.extensions import db


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(float(lat1)), math.radians(float(lat2))
    dlat = phi2 - phi1
    dlon = math.radians(float(lon2) - float(lon1))
    a = math.sin(dlat / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def get_user_preferences(user: User):
    try:
        return json.loads(user.preferences) if user.preferences else []
    except:
        return []


def weighted_score(poi: POI, preferences: list[str]):
    try:
        poi_tags = json.loads(poi.tags) if poi.tags else []
    except:
        poi_tags = []

    match_count = len(set(preferences) & set(poi_tags))
    match_score = match_count / len(preferences) if preferences else 0
    rating = float(poi.rating) if poi.rating is not None else 0.0

    return 0.7 * match_score + 0.3 * rating


def get_similar_users(user_id):
    user_history = UserPOIHistory.query.filter_by(user_id=user_id).all()
    user_pois = set(h.poi_id for h in user_history)
    if not user_pois:
        return []

    all_histories = UserPOIHistory.query.filter(UserPOIHistory.user_id != user_id).all()
    user_map = {}
    for h in all_histories:
        user_map.setdefault(h.user_id, set()).add(h.poi_id)

    similarities = []
    for other_user, pois in user_map.items():
        intersection = len(user_pois & pois)
        union = len(user_pois | pois)
        if union > 0:
            score = intersection / union
            similarities.append((other_user, score))

    similarities.sort(key=lambda x: x[1], reverse=True)
    return [u for u, sim in similarities[:5]]


def collaborative_filtering(user_id, user_lat, user_lon, radius_km=50):
    similar_users = get_similar_users(user_id)
    if not similar_users:
        return []

    poi_counter = Counter()
    for uid in similar_users:
        his = UserPOIHistory.query.filter_by(user_id=uid).all()
        for h in his:
            poi_counter[h.poi_id] += 1

    user_visited = set(h.poi_id for h in UserPOIHistory.query.filter_by(user_id=user_id).all())

    candidates = [
        (poi_id, count)
        for poi_id, count in poi_counter.items()
        if poi_id not in user_visited
    ]

    recommendations = []
    for poi_id, count in sorted(candidates, key=lambda x: x[1], reverse=True):
        poi = POI.query.get(poi_id)
        if poi:
            try:
                distance = haversine(user_lat, user_lon, poi.latitude, poi.longitude)
                if distance > radius_km:
                    continue  # 🚫 跳过超过范围的协同推荐
            except:
                continue

            distance = haversine(user_lat, user_lon, poi.latitude, poi.longitude)
            recommendations.append({
                'id': poi.id,
                'name': poi.name,
                'category': poi.category,
                'description': poi.description,
                'lat': float(poi.latitude),
                'lng': float(poi.longitude),
                'rating': float(poi.rating or 4.0),  # 如果没评分就用默认4.0
                'score': round(0.5 + count * 0.1, 4),
                'distance': round(distance, 2),  # ✅ 正确计算真实距离
                'reason': '协同推荐'
            })

    return recommendations


def recommend_poi(user_id, user_lat, user_lon, radius_km=50):
    user = User.query.get(user_id)
    if not user:
        return []

    preferences = get_user_preferences(user)
    pois = POI.query.all()
    results = []

    for poi in pois:
        try:
            distance = haversine(user_lat, user_lon, poi.latitude, poi.longitude)
        except:
            continue

        if distance <= radius_km:
            score = weighted_score(poi, preferences)
            results.append({
                'id': poi.id,
                'name': poi.name,
                'category': poi.category,
                'description': poi.description,
                'lat': float(poi.latitude),
                'lng': float(poi.longitude),
                'rating': float(poi.rating or 0),
                'score': round(score, 4),
                'distance': round(distance, 2),
                'reason': '偏好推荐'
            })

    results.sort(key=lambda x: x['score'], reverse=True)
    collab = collaborative_filtering(user_id, user_lat, user_lon, radius_km)
    results += collab[:3]

    return results
