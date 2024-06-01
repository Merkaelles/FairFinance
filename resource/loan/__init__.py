from flask import Blueprint
from flask_restful import Api
from utils.output import output_json

loan_bp = Blueprint('loan', __name__, url_prefix='/loan')
loan_api = Api(loan_bp)
loan_api.representation('application/json')(output_json)

from .loan_rs import *
loan_api.add_resource(Loan_Apply, '/loan', endpoint='loan')
loan_api.add_resource(MyLoan, '/myLoan', endpoint='myLoan')
loan_api.add_resource(Debt, '/debt', endpoint='debt')
loan_api.add_resource(Repayment, '/repay', endpoint='repay')