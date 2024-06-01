from models import db
from sqlalchemy import ForeignKey
from datetime import datetime


class Loan(db.Model):
    __tablename__ = 'loan'
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    loanAmount = db.Column(db.Float(8, 2), comment='借款金额')
    lUid = db.Column(db.BIGINT, ForeignKey('user.id'), comment='用户id')
    user = db.relationship('User', backref=db.backref('loan', lazy=True))
    duration = db.Column(db.Integer, comment='借款时长')
    lName = db.Column(db.String(64), comment='借款人姓名')
    lRepayType = db.Column(db.Integer, comment='还款模式', default=1)  # 1 等额本金 0 先息后本
    lRate = db.Column(db.Float(4, 2), comment='借款利率')
    lRepayDay = db.Column(db.Integer, comment='还款日', default=10)
    status = db.Column(db.Integer, comment='审批状态', default=0)  # 0未审批 1通过 2驳回
    applyDate = db.Column(db.DateTime, default=datetime.now, comment='申请时间')


class DebtInfo(db.Model):
    __tablename__ = 'debt_info'
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    debtNo = db.Column(db.String(128), comment='债权编号')
    loanNo = db.Column(db.BIGINT, ForeignKey('loan.id'), comment='借款id')
    loan = db.relationship('Loan', backref=db.backref('debt_info', lazy=True, uselist=False))
    debtorsName = db.Column(db.String(64), comment='债务人名称')
    debtorsId = db.Column(db.String(128), comment='债务人身份证号')
    loanPurpose = db.Column(db.String(128), comment='借款用途')
    loanType = db.Column(db.Integer, comment='借款类型')
    loanStartDate = db.Column(db.DateTime, comment='原始借款开始日期')
    loanPeriod = db.Column(db.Integer, comment='原始借款期限')
    loanEndDate = db.Column(db.Date, comment='原始借款到期日期')
    repayStyle = db.Column(db.Integer, comment='还款方式')
    repayDate = db.Column(db.Integer, comment='还款日')
    repayMoney = db.Column(db.Float(8, 2), comment='还款金额')
    debtMoney = db.Column(db.Float(8, 2), comment='债权金额')
    debtYearRate = db.Column(db.Float(4, 2), comment='债权年化利率')
    debtMonthRate = db.Column(db.Float(4, 2), comment='债权月利率')
    debtTransferMoney = db.Column(db.Float(8, 2), comment='债权转入金额')
    debtTransferDate = db.Column(db.Date, comment='债权转入日期')
    debtTransferredPeriod = db.Column(db.Date, comment='债权转入期限')
    debtTransferOutDate = db.Column(db.Date, comment='债权转出日期')
    creditor = db.Column(db.String(64), comment='债权人')
    debtStatus = db.Column(db.Integer, comment='债权状态')
    borrowerId = db.Column(db.BIGINT, ForeignKey('user.id'), comment='借款人ID')
    user = db.relationship('User', backref=db.backref('debt_info', lazy=True, uselist=False))
    availablePeriod = db.Column(db.Integer, comment='可用金额')
    matchedMoney = db.Column(db.Float(8, 2), comment='已匹配金额')
    matchedStatus = db.Column(db.Integer, comment='匹配状态')  # 0 未匹配  1 部分匹配  2 完全匹配
    repaymentStyleName = db.Column(db.String(64), comment='还款方式名称')
    debtStatusName = db.Column(db.String(64), comment='债权状态名字')
    matchedStatusName = db.Column(db.String(64), comment='匹配状态名称')
    debtType = db.Column(db.Integer, comment='标的类型')
    debtTypeName = db.Column(db.String(64), comment='标的类型名称')


class Repay(db.Model):
    __tablename__ = 'repay'
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True, comment='主键')
    claimsId = db.Column(db.BIGINT, ForeignKey('debt_info.id'), comment='债权id')
    debtInfo = db.relationship('DebtInfo', backref=db.backref('repay', lazy=True))
    receivableDate = db.Column(db.DateTime, comment='应还日期')
    receivableMoney = db.Column(db.Float(8, 2), comment='应还余额')
    currentTerm = db.Column(db.Integer, comment='当前还款期')
    recordDate = db.Column(db.DateTime, comment='记录日期')
    isReturned = db.Column(db.Integer, default=0, comment='是否还款')  # 0未还款 1已还款



