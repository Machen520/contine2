from flask import Blueprint, request, jsonify, session
from app.models import User
from app.extensions import db
from app.models import UserPOIHistory, POI
import json

user_bp = Blueprint('user', __name__)


@user_bp.route('/preferences', methods=['POST'])
def update_preferences():
    if 'user_id' not in session:
        return jsonify({'code': 401, 'msg': '未登录'})

    data = request.get_json()
    preferences = data.get('preferences', [])
    user = User.query.get(session['user_id'])
    user.preferences = json.dumps(preferences)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '更新成功'})


@user_bp.route('/history', methods=['POST'])
def record_history():
    if 'user_id' not in session:
        return jsonify({'code': 401, 'msg': '未登录'})

    data = request.get_json()
    poi_id = data.get('poi_id')

    if not poi_id:
        return jsonify({'code': 400, 'msg': '缺少 poi_id'})

    record = UserPOIHistory(user_id=session['user_id'], poi_id=poi_id)
    db.session.add(record)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '访问记录成功'})


@user_bp.route('/history/list', methods=['GET'])
def get_history():
    if 'user_id' not in session:
        return jsonify({'code': 401, 'msg': '未登录'})

    user_id = session['user_id']
    history = (
        db.session.query(UserPOIHistory, POI)
        .join(POI, POI.id == UserPOIHistory.poi_id)
        .filter(UserPOIHistory.user_id == user_id)
        .order_by(UserPOIHistory.visit_time.desc())
        .limit(50)
        .all()
    )

    result = []
    for h, poi in history:
        result.append({
            'poi_id': poi.id,
            'name': poi.name,
            'category': poi.category,
            'visit_time': h.visit_time.strftime('%Y-%m-%d %H:%M:%S'),
            'lat': poi.latitude,
            'lng': poi.longitude
        })

    return jsonify({'code': 200, 'data': result})
