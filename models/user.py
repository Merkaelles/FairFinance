from datetime import datetime
from sqlalchemy import ForeignKey
from models import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), comment='用户名')
    password = db.Column(db.String(255), comment='密码')
    payPassword = db.Column(db.String(255), comment='支付密码')
    payPwdStatus = db.Column(db.Integer, comment='支付密码验证', default=0)  # 1代表已经验证
    email = db.Column(db.String(100), comment='邮箱')
    emailStatus = db.Column(db.Integer, comment='邮箱验证', default=0)  # 1代表已经验证
    inviteId = db.Column(db.String(64), comment='邀请码')
    ip = db.Column(db.String(128), comment='ip')
    phone = db.Column(db.String(11), comment='手机号')
    onlock = db.Column(db.Integer, comment='用户状态', default=0)  # 0代表正常
    phoneStatus = db.Column(db.Integer, comment='手机验证', default=1)  # 1代表已经验证
    realName = db.Column(db.String(64), comment='真实姓名')
    remark = db.Column(db.String(500), comment='备注')
    realNameStatus = db.Column(db.Integer, comment='实名认证', default=0)  # 1代表已经验证
    nick_name = db.Column(db.String(200), comment='昵称')
    avatar = db.Column(db.String(128), comment='头像')
    idNum = db.Column(db.String(64), comment='身份证号码')
    sumFriends = db.Column(db.Integer, comment='邀请数量统计', default=0)
    invited_by_id = db.Column(db.Integer, comment='邀请我的用户ID')
    role = db.Column(db.Integer, comment='是否管理员', default=0)  # 0普通用户  1代码管理员

    loginTime = db.Column(db.DateTime, default=datetime.now(), comment='登录时间')
    registerTime = db.Column(db.DateTime, default=datetime.now(), comment='用户注册的时间')

    @property
    def pwd(self):
        return self.password

    @pwd.setter
    def pwd(self, password_x):
        self.password = generate_password_hash(password_x)

    def check_password(self, password_x):
        return check_password_hash(self.password, password_x)

    @property
    def pay_pwd(self):
        return self.payPassword

    @pay_pwd.setter
    def pay_pwd(self, pay_password_x):
        self.payPassword = generate_password_hash(pay_password_x)

    def check_pay_password(self, pay_password_x):
        return check_password_hash(self.payPassword, pay_password_x)


class Account(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.BIGINT, ForeignKey('user.id'), comment='用户表主键')
    user = db.relationship('User', backref=db.backref('account', lazy=True, uselist=False))
    total = db.Column(db.Float(10, 2), comment='帐户总额', default=0)
    balance = db.Column(db.Float(10, 2), comment='帐户可用余额', default=0)
    frozen = db.Column(db.Float(10, 2), comment='账户总计冻结总额', default=0)
    investmentW = db.Column(db.Float(10, 2), comment='总计待收本金', default=0)
    interestTotal = db.Column(db.Float(10, 2), comment='总计待收利息', default=0)
    addCapitalTotal = db.Column(db.Float(10, 2), comment='月投总额', default=0)
    recyclingInterest = db.Column(db.Float(10, 2), comment='月取总额', default=0)
    capitalTotal = db.Column(db.Float(10, 2), comment='月剩总额', default=0)
    investmentA = db.Column(db.Float(10, 2), comment='已投资总额', default=0)
    interestA = db.Column(db.Float(10, 2), comment='已赚取利息', default=0)
    uApplyExtractMoney = db.Column(db.Float(10, 2), comment='申请提现金额', default=0)
    discount = db.Column(db.Float(8, 2), comment='代金券的总金额', default=0)


class Bankcard(db.Model):
    __tablename__ = 'bankcard'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bankCardNum = db.Column(db.String(64), comment='银行卡号')
    holder = db.Column(db.String(64), comment='账户名')
    openingBank = db.Column(db.String(64), comment='开户银行')
    cityId = db.Column(db.Integer, comment='城市id')
    userId = db.Column(db.BIGINT, ForeignKey('user.id'), comment='用户表主键')
    user = db.relationship('User', backref=db.backref('bankcard', lazy=True))
    bankId = db.Column(db.Integer, comment='银行编号')
    bankBranch = db.Column(db.String(64), comment='银行支行')
    boundPhone = db.Column(db.String(64), comment='绑定手机号码')