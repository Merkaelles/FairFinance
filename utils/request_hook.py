from .token import verify_token
from flask import g, request


def jwt_request_auth():
    g.user_id = None
    token = request.headers.get('token')
    if token:
        data = verify_token(token)
        if 'id' in data:
            g.user_id = data['id']

