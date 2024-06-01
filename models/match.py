from datetime import datetime
from models import db
from sqlalchemy import ForeignKey


class Funding_not_matched(db.Model):
    __tablename__ = 'funds_not_matched'
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True, comment='主键')
    InvestRecordId = db.Column(db.BIGINT, ForeignKey('invest_record.id'), comment='投资记录')
    invest_record = db.relationship('Invest_Record', backref=db.backref('fundsNotMatched', lazy=True))
    NotMatchedMoney = db.Column(db.Float(8, 2), comment='待匹配金额')
    FundsType = db.Column(db.Integer, comment='资金类型', default=1)
    FundsWeight = db.Column(db.Float(8, 2), comment='资金')
    matchedStatus = db.Column(db.Integer, comment='匹配状态')     # 0 未匹配  1 部分匹配  2 完全匹配
    CreateDate = db.Column(db.DateTime, comment='创建时间', default=datetime.now())


class Matched_Result(db.Model):
    __tablename__ = 'matched_result'
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True, comment='主键')
    userId = db.Column(db.BIGINT, ForeignKey('user.id'), comment='用户id')
    user = db.relationship('User', backref=db.backref('matched_result', lazy=True))
    debtId = db.Column(db.BIGINT, ForeignKey('debt_info.id'), comment='债权id')
    debt_info = db.relationship('DebtInfo', backref=db.backref('matched_result', lazy=True))
    investId = db.Column(db.BIGINT, ForeignKey('invest_record.id'), comment='投资记录主键')
    invest_record = db.relationship('Invest_Record', backref=db.backref('matched_result', lazy=True))
    transferSerialNo = db.Column(db.String(100), comment='交易流水号')
    purchaseMoney = db.Column(db.Float(8, 2), comment='购买金额（匹配金额）', default=0)
    confirmedDate = db.Column(db.DateTime, comment='购买理财或者借款确认的日期')
    isConfirmed = db.Column(db.Integer, comment='是否确认', default=0)
    matchDate = db.Column(db.DateTime, comment='匹配上的日期', default=3)
    fundType = db.Column(db.Integer, comment='资金类型')
    debtType = db.Column(db.Integer, comment='债权类型')
    isExecuted = db.Column(db.Integer, comment='是否清算过')
