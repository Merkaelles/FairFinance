from models import db
from sqlalchemy import ForeignKey
from datetime import datetime


class Product(db.Model):
    __tablename__ = 't_product'
    proId = db.Column(db.BIGINT, primary_key=True, autoincrement=True, comment='产品id')
    productName = db.Column(db.String(100), comment='产品名称')
    closedPeriod = db.Column(db.BIGINT, comment='转让封闭期', default=12)
    earlyRedeptionType = db.Column(db.Integer, comment='提前赎回类型', default=1)
    earningType = db.Column(db.Integer, comment='收益利率类型', default=134)  # 年利率是134 ，其他是月利率
    investRule = db.Column(db.Integer, comment='数量规则', default=10)
    isAllowTransfer = db.Column(db.Integer, comment='是否可转让', default=0)
    isRepeatInvest = db.Column(db.Integer, comment='是否复投', default=0)
    lowerTimeLimit = db.Column(db.Integer, comment='产品最低期限', default=3)
    proLowerInvest = db.Column(db.BIGINT, comment='产品起投金额', default=1000)
    proNum = db.Column(db.String(100), comment='产品编号')
    proUpperInvest = db.Column(db.BIGINT, comment='产品投资上限', default=300000)
    proTypeId = db.Column(db.Integer, comment='产品类型', default=1)
    status = db.Column(db.Integer, comment='状态', default=1)  # (1:表示正常；0：表示停用)
    upperTimeLimit = db.Column(db.Integer, comment='产品最大期限', default=36)
    wayToReturnMoney = db.Column(db.Integer, comment='回款方式', default=109)  # （109：表示一次性回款 ，110：每月提取，到期退出）


class Product_Rate(db.Model):
    __tablename__ = 't_product_rate'
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True, comment='编号')
    incomeRate = db.Column(db.Float(4, 2), comment='利率值')
    month = db.Column(db.Integer, comment='月份', default=12)
    productId = db.Column(db.BIGINT, ForeignKey('t_product.proId'), comment='产品编号')
    product = db.relationship('Product', backref=db.backref('rate', lazy=True))


class Expected_Return(db.Model):
    __tablename__ = 'expected_return'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.BIGINT, ForeignKey('user.id'), comment='用户ID')
    productId = db.Column(db.BIGINT, ForeignKey('t_product.proId'), comment='产品ID')
    product = db.relationship('Product')
    investRecord = db.Column(db.BIGINT, ForeignKey('invest_record.id'), comment='投资记录ID')
    expectedDate = db.Column(db.DateTime, comment='收益日期')
    expectedMoney = db.Column(db.Float(8, 2), comment='收益金额', default=0)
    createDate = db.Column(db.DateTime, default=datetime.now(), comment='创建日期')
