from flask import Blueprint
from flask_restful import Api
from utils.output import output_json

match_bp = Blueprint('match', __name__, url_prefix='/match')
match_api = Api(match_bp)
match_api.representation('application/json')(output_json)

from .match_rs import *
match_api.add_resource(Matching, '/match', endpoint='match')
match_api.add_resource(Matches, '/matches', endpoint='matches')
match_api.add_resource(MatchedResults, '/results', endpoint='results')
match_api.add_resource(Returns, '/returns', endpoint='returns')
match_api.add_resource(Invest_Income, '/income', endpoint='income')
