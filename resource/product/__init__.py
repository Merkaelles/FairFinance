from flask import Blueprint
from flask_restful import Api
from utils.output import output_json

product_bp = Blueprint('product', __name__, url_prefix='/product')
product_api = Api(product_bp)
product_api.representation('application/json')(output_json)

from .product_rs import *
product_api.add_resource(Product_Display, '/products', endpoint='products')
product_api.add_resource(ProductRate_Query, '/product_rate', endpoint='product_rate')
product_api.add_resource(Invest, '/invest', endpoint='invest')
product_api.add_resource(Deal, '/deal', endpoint='deal')