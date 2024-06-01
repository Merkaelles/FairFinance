import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
from flask import current_app
from models.user import User
from resource import const


def generate_token(uid):
    payload = {
        'id': uid,
        'exp': datetime.utcnow() + timedelta(seconds=const.JWT_EXPIRE_TIME)
    }
    return jwt.encode(payload, key=const.SECRET_KEY, algorithm='HS256')


def verify_token(token):
    try:
        data = jwt.decode(token, key=const.SECRET_KEY, algorithms='HS256')
        current_app.logger.info(data)
        u = User.query.filter(User.id == data['id']).first()
        if u and u.onlock == 0:
            return {'id': u.id}
        else:
            return {'message': 'Login expired'}
    except PyJWTError as e:
        current_app.logger.error(e)
        return {'message': 'token verification failed'}