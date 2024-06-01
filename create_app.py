from flask import Flask
from flask_migrate import Migrate


def create_app(env):
    app = Flask(__name__)
    app.config.from_object(env)

    from models import db
    db.init_app(app)

    from utils.cache_redis import redis_cli
    redis_cli.init_app(app)

    from utils.logger import create_logger
    create_logger(app)

    Migrate(app, db)   # flask 命令映射迁移: flask db init --> flask db migrate --> flask db upgrade

    from utils.limiter import limiter
    limiter.init_app(app)

    from utils.request_hook import jwt_request_auth
    app.before_request(jwt_request_auth)

    from resource.user import user_bp
    from resource.product import product_bp
    from resource.loan import loan_bp
    from resource.match import match_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(loan_bp)
    app.register_blueprint(match_bp)

    return app
