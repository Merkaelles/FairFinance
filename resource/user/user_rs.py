import json
import random
import string

from flask_restful import Resource
from flask import g, request, current_app
from flask_restful.reqparse import RequestParser

from models import db
from models.record import Deal_Record
from models.user import User, Account, Bankcard
from utils.sms import send_sms
from utils.limiter import limiter
from flask_limiter.util import get_remote_address
from utils.cache_redis import redis_cli
from resource import const
from utils.token import generate_token
from utils.decorators import login_required
from models.message import Message, Message_Content
from resource.user.Message_Serializer import MessagePaginatorSerializer
from resource.user.Account_Serializer import AccountSerializer, BankcardSerializer, UserInfoSerializer, \
    InviteListSerializer
from utils.transaction_tool import generate_transaction_id


class Test(Resource):
    def get(self):
        return {'香巴拉': '世界尽头', 'current_id': g.user_id}

    def post(self):
        n = request.json.get('number')
        print('获取参数', n)
        return {'number': n}


class IsExistingPhone(Resource):
    def get(self):
        phone = request.args.get('phone')
        u = User.query.filter(User.phone == phone).first()
        if u:
            return {'message': 'The phone number has been used', 'code': 201}
        return {'msg': 'OK'}


class User_SMS(Resource):
    decorators = [
        limiter.limit(const.LIMIT_SMS_CODE_BY_PHONE, key_func=lambda: request.args['phone'],
                      error_message='request auth code over frequently'),
        limiter.limit(const.LIMIT_SMS_CODE_BY_IP, key_func=get_remote_address,
                      error_message='request auth code over frequently')
    ]

    def get(self):
        phone = request.args.get('phone').strip()
        code = random.randint(100000, 900000)
        result = send_sms(phone, code)
        result = json.loads(result)
        if result['Message'] != 'OK':
            print(result)
        else:
            current_app.logger.info('发送验证码成功， target phone:{}'.format(phone))
            result['phone'] = phone
            redis_cli.setex("auth code to {}".format(phone), const.SMS_VERIFY_CODE_EXPIRE, code)
            return result


class Register(Resource):
    def post(self):
        rp = RequestParser()
        rp.add_argument('phone', required=True)
        rp.add_argument('username', required=True)
        rp.add_argument('password', required=True)
        rp.add_argument('auth_code', required=True)
        rp.add_argument('invite_code')
        args = rp.parse_args()
        phone = args.phone
        username = args.username
        password = args.password
        auth_code = args.auth_code
        invite_code = args.invite_code

        u = User.query.filter(User.username == username).first()
        if u:
            current_app.logger.info(f'{username}: The username has been used')
            return {'message': 'duplicated username', 'code': 201}
        auth_code_x = redis_cli.get(f'auth code to {phone}').decode()

        if not auth_code_x:
            current_app.logger.info('The auth code expired')
            return {'message': 'The auth code expired', 'code': 201}
        elif auth_code != auth_code_x:
            current_app.logger.info('The auth code is wrong')
            return {'message': 'The auth code is wrong', 'code': 201}

        inviteId = self.generate_inviteId()
        u = User(username=username, pwd=password, phone=phone, inviteId=inviteId)

        if invite_code:
            self.check_invite(u, invite_code)
        try:
            db.session.add(u)
            db.session.flush()  # 把数据插入缓冲区（get id）
            account = Account(userId=u.id)
            db.session.add(account)
            db.session.commit()
            return {'msg': 'register user-account finished'}
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return {'message': 'registration failed', 'code': 201}

    def generate_inviteId(self):
        flag = True
        inviteId = None
        while flag:
            inviteId = ''.join(random.sample(string.ascii_uppercase + string.digits, 5))
            u = User.query.filter(User.inviteId == inviteId).first()
            if not u:
                flag = False
        return inviteId

    def check_invite(self, user, invite_code):
        u = User.query.filter(User.inviteId == invite_code.strip()).first()
        if u:
            user.invited_by_id = u.id
            u.account.discount += const.INVITE_BONUS
            u.sumFriends = u.sumFriends + 1 if u.sumFriends else 1


class Login(Resource):
    def post(self):
        rp = RequestParser()
        rp.add_argument('username', required=True)
        rp.add_argument('password', required=True)
        args = rp.parse_args()
        u = User.query.filter(User.username == args.username).first()
        if not u:
            return {'message': 'This user did not register', 'code': 201}
        if not u.check_password(args.password):
            return {'message': 'Wrong password', 'code': 201}
        else:
            token = generate_token(u.id)
            current_app.logger.info(token)
            return {'msg': 'Login pass', 'token': token}


class Logout(Resource):
    def get(self):
        if not g.user_id:
            g.user_id = None
        return {'msg': 'Logout finished'}


class User_Avatar(Resource):
    method_decorators = [login_required]

    def post(self):
        avatar = request.files['avatar']
        avatar_dir = current_app.config['AVATAR_DIR']
        avatar_path = avatar_dir + '/' + f'{g.user_id}' + '_' + avatar.filename
        avatar.save(avatar_path)
        u = User.query.filter(User.id == g.user_id).first()
        if u:
            u.avatar = avatar_path
            db.session.commit()
            return {'msg': 'User avatar uploading finished', 'avatar': avatar_path}


class Set_PayPwd(Resource):
    method_decorators = [login_required]

    def post(self):
        rp = RequestParser()
        rp.add_argument('pay_pwd', required=True, location='form')
        args = rp.parse_args()
        pay_pwd = args.pay_pwd
        u = User.query.filter(User.id == g.user_id).first()
        if u:
            u.pay_pwd = pay_pwd
            u.emailStatus = 1
            db.session.commit()
            return {'msg': 'Set pay password successfully'}


class User_Info(Resource):
    method_decorators = [login_required]

    def get(self):
        user = User.query.filter(User.id == g.user_id).first()
        user_info_data = UserInfoSerializer(user).to_dict()
        account = Account.query.filter(Account.userId == g.user_id).first()
        account_date = {}
        if account:
            account_date = AccountSerializer(account).to_dict()

        return {'role': ['admin'] if user.role else ['user'],
                'username': user.username,
                'userInfoData': user_info_data,
                'accountInfo': account_date
                }


class Message_Box(Resource):
    def post(self):
        rp = RequestParser()
        rp.add_argument('title', required=True, location='form')
        rp.add_argument('content', required=True, location='form')
        rp.add_argument('group', location='form')
        rp.add_argument('receiverID', location='form')
        args = rp.parse_args()
        title = args.title
        content = args.content
        group = int(args.group)
        receiverID = args.receiverID

        receiver_list = []

        if group == 0 or group == 1:
            receiver_list = User.query.filter(User.role == group).all()
        elif group == 2:
            receiver_list = User.query.all()
        elif receiverID:
            receiver = User.query.filter(User.id == receiverID).first()
            if not receiver:
                return {'message': 'Please specify receiver'}
            else:
                receiver_list = [receiver]

        u = User.query.filter(User.id == g.user_id).first()

        message_content = Message_Content(title=title, content=content)
        db.session.add(message_content)
        db.session.flush()
        for receiver in receiver_list:
            message_box = Message(sender=u.username, receiverID=receiver.id, content_id=message_content.id)
            db.session.add(message_box)
        db.session.commit()
        return {'msg': 'send finished'}

    def get(self):
        u = User.query.filter(User.id == g.user_id).first()
        rp = RequestParser()
        rp.add_argument('page', required=True, location='args')
        rp.add_argument('per_page', required=True, location='args')
        args = rp.parse_args()
        page = int(args.page)
        per_page = int(args.per_page)
        message_paginator = Message.query.filter(Message.receiverID == g.user_id).paginate(page=page, per_page=per_page,
                                                                                           error_out=False)
        messages_data = MessagePaginatorSerializer(message_paginator).to_dict()
        return {'msg': 'OK', 'messages_data': messages_data}

    def put(self):
        rp = RequestParser()
        rp.add_argument('messageId', required=True, location='args')
        args = rp.parse_args()
        messageId = args.messageId
        message = Message.query.filter(id == messageId).first()
        if message:
            message.read_state = 1
            db.session.commit()
            return {'msg': 'OK'}
        return {'message': 'No this message', 'code': 201}

    def delete(self):
        rp = RequestParser()
        rp.add_argument('messageId', required=True, location='args')
        args = rp.parse_args()
        messageId = args.messageId
        message = Message.query.filter(id == messageId).first()
        if message:
            message.delete()
            db.session.commit()
            return {'msg': 'OK'}
        return {'message': 'No this message', 'code': 201}


class Bankcard_Manager(Resource):
    # method_decorators = [login_required]

    def post(self):
        u = User.query.filter(User.id == g.user_id).first()
        rp = RequestParser()
        rp.add_argument('openingBank', required=True, location='form')
        rp.add_argument('bankBranch', required=True, location='form')
        rp.add_argument('cityId', required=True, location='form')
        rp.add_argument('bankCardNum', required=True, location='form')
        args = rp.parse_args()
        openingBank = args.openingBank
        bankBranch = args.bankBranch
        cityId = args.cityId
        bankCardNum = args.bankCardNum
        bc = Bankcard.query.filter(Bankcard.bankCardNum == bankCardNum).first()
        if bc:
            return {'message': 'The bankcard has been added, please dont add again', 'code': 201}
        u = User.query.filter(User.id == g.user_id).first()
        bankcard = Bankcard(bankCardNum=bankCardNum, openingBank=openingBank, userId=u.id, holder=u.username,
                            bankBranch=bankBranch,
                            cityId=cityId)
        db.session.add(bankcard)
        db.session.commit()
        return {'msg': 'Add finished'}

    def get(self):
        bankcards = Bankcard.query.filter(Bankcard.userId == g.user_id).all()
        if bankcards:
            return {'msg': 'Query finished', 'bankcards': BankcardSerializer(bankcards).to_dict()}
        return {'message': 'The account has no bankcards'}

    def delete(self):
        rp = RequestParser()
        rp.add_argument('bankCardNum', required=True, location='args')
        args = rp.parse_args()
        bc = Bankcard.query.filter(Bankcard.bankCardNum == args.bankCardNum).first()
        if bc:
            bc.delete()
            db.session.commit()
            return {'msg': 'Delete finished'}
        return {'message': 'No this bankcard', 'code': 201}


class Account_Manager(Resource):
    method_decorators = [login_required]

    def get(self):
        a = Account.query.filter(Account.userId == g.user_id).first()
        if a:
            account_data = AccountSerializer(a).to_dict()
            return {'msg': 'OK', 'account_data': account_data}
        return {'message': 'No this account', 'code': 400}, 400


class Account_Recharge(Resource):
    method_decorators = [login_required]

    def post(self):
        rp = RequestParser()
        rp.add_argument('amount', required=True, location='form')
        rp.add_argument('bankcard', required=True, location='form')
        args = rp.parse_args()
        amount = float(args.amount)
        bankcard = args.bankcard
        a = Account.query.filter(Account.userId == g.user_id).first()
        if a:
            before_balance = a.balance
            a.balance = float(before_balance) + amount
            a.total = float(a.total) + amount
            recharge_id = generate_transaction_id(const.DealType.recharge.name)
            deal_record = Deal_Record(aUserId=g.user_id, aReceiveOrPay=0, aTransferSerialNo=recharge_id,
                                      aTransferStatus=1, aBeforeTradingMoney=before_balance, aAmount=amount,
                                      aAfterTradingMoney=a.balance, aDescription='充值',
                                      aType=const.DealType.recharge.value)
            db.session.add(deal_record)
            db.session.commit()
            return {'msg': 'Recharge finished'}
        return {'message': 'No this account', 'code': 400}


class Account_Withdrawal(Resource):
    method_decorators = [login_required]

    def post(self):
        rp = RequestParser()
        rp.add_argument('amount', required=True, location='form')
        rp.add_argument('card_id', required=True, location='form')
        rp.add_argument('payPwd', required=True, location='form')
        args = rp.parse_args()
        amount = float(args.amount)
        card_id = args.card_id
        pay_pwd = args.payPwd
        u = User.query.filter(User.id == g.user_id).first()
        if not u.check_pay_password(pay_pwd):
            return {'message': '支付密码错误', 'code': 201}

        a = Account.query.filter(Account.userId == g.user_id).first()
        if a:
            if a.balance < amount:
                return {'message': '超出了可提取的金额', 'code': 201}, 400
            else:
                before_balance = a.balance
                a.balance = float(a.balance) - amount
                a.total = float(a.total) - amount
                deal_id = generate_transaction_id(const.DealType.extract.name)
                deal_record = Deal_Record(aUserId=g.user_id, aReceiveOrPay=1, aTransferSerialNo=deal_id,
                                          aTransferStatus=1, aBeforeTradingMoney=before_balance, aAmount=amount,
                                          aAfterTradingMoney=a.balance, aDescription='提现',
                                          aType=const.DealType.extract.value)
                db.session.add(deal_record)
                db.session.commit()
                return {'msg': 'Withdrawal finished'}


class InviteList(Resource):
    def get(self):
        invite_list = User.query.filter(User.invite_user_id == g.user_id).all()
        if invite_list:
            data = InviteListSerializer(invite_list).to_dict()
            return {'msg': 'success', 'invite_list': data}
        else:
            return {'msg': 'success', 'invite_list': []}


class RealName(Resource):
    method_decorators = [login_required]

    def post(self):
        rp = RequestParser()
        rp.add_argument('realName', required=True)
        rp.add_argument('idNum', required=True)
        args = rp.parse_args()
        realName = args.realName   # 真实姓名
        idNum = args.idNum         # 身份证ID
        user = User.query.filter(User.id == g.user_id).first()
        if user.realName:
            return {"code": 201, 'message': '不可重复验证'}
        else:
            user.realName = realName  # 名字
            user.realNameStatus = 1  # 实名状态
            user.idNum = idNum  # 身份证
            db.session.commit()
            return {'msg': 'success'}