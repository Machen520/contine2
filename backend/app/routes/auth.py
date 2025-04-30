import json

from flask import Blueprint, request, jsonify, session
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    preferences = data.get('preferences', [])

    if not username or not password:
        return jsonify({'code': 400, 'msg': '用户名或密码不能为空'})

    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'msg': '用户名已存在'})

    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        preferences=json.dumps(preferences)
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '注册成功'})


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        return jsonify({'code': 200, 'msg': '登录成功', 'user_id': user.id})
    return jsonify({'code': 401, 'msg': '用户名或密码错误'})


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'code': 200, 'msg': '已退出登录'})


@auth_bp.route('/userinfo', methods=['GET'])
def user_info():
    if 'user_id' not in session:
        return jsonify({'code': 401, 'msg': '未登录'})
    user = User.query.get(session['user_id'])
    return jsonify({'code': 200, 'username': user.username})
