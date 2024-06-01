from flask import Blueprint
from flask_restful import Api
from utils.output import output_json

user_bp = Blueprint('user', __name__, url_prefix='/user')
user_api = Api(user_bp)
user_api.representation('application/json')(output_json)

from .user_rs import *
user_api.add_resource(Test, '/')
user_api.add_resource(IsExistingPhone, '/isExistingPhone', endpoint='isExistingPhone')
user_api.add_resource(User_SMS, '/sms', endpoint='sms')
user_api.add_resource(Register, '/register', endpoint='register')
user_api.add_resource(Login, '/login', endpoint='login')
user_api.add_resource(Logout, '/logout', endpoint='logout')
user_api.add_resource(User_Avatar, '/avatar', endpoint='avatar')
user_api.add_resource(Set_PayPwd, '/setPayPwd', endpoint='setPayPwd')
user_api.add_resource(User_Info, '/info', endpoint='info')
user_api.add_resource(Message_Box, '/message', endpoint='message')
user_api.add_resource(Bankcard_Manager, '/bankcard', endpoint='bankcard')
user_api.add_resource(Account_Manager, '/account', endpoint='account')
user_api.add_resource(Account_Recharge, '/recharge', endpoint='recharge')
user_api.add_resource(Account_Withdrawal, '/withdrawal', endpoint='withdrawal')
user_api.add_resource(InviteList, '/inviteList', endpoint='inviteList')
user_api.add_resource(RealName, '/realName', endpoint='realName')