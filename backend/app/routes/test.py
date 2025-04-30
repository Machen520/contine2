# app/routes/test.py
from flask import Blueprint

test_bp = Blueprint('test', __name__)


@test_bp.route('/')
def hello():
    return "Flask 后端运行成功！"
