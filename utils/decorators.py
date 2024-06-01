from flask import g


def login_required(func):
    def wrapper(*args, **kwargs):
        if not g.user_id:
            return {'message': 'This operation required login'}, 401
        return func(*args, **kwargs)

    return wrapper
