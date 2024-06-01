from models import db
from sqlalchemy import ForeignKey
from datetime import datetime


class Invest_Record(db.Model):
    __tablename__ = 'invest_record'
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True, comment='主键')
    pProductId = db.Column(db.BIGINT, ForeignKey('t_product.proId'), comment='产品id')
    product = db.relationship('Product', backref=db.backref('invest_record', lazy=True))
    pUid = db.Column(db.BIGINT, ForeignKey('user.id'), comment='用户id')
    user = db.relationship('User', backref=db.backref('invest_record', lazy=True))
    pSerialNo = db.Column(db.String(64), comment='投资编号')
    pBeginDate = db.Column(db.DateTime, default=datetime.now(), comment='加入日期')
    pEndDate = db.Column(db.DateTime, comment='到期日期')
    pRedeemDate = db.Column(db.DateTime, comment='赎回日期')
    pMatchDate = db.Column(db.DateTime, comment='匹配日期')
    pAmount = db.Column(db.Float(8, 2), comment='金额')
    pDate = db.Column(db.DateTime, default=datetime.now(), comment='系统时间')
    pProductType = db.Column(db.Integer, comment='收益利率类型', default=0)
    pEarningsType = db.Column(db.String(100), comment='产品编号')
    pEarnings = db.Column(db.Float(4, 2), comment='收益率')
    pAdvanceRedemption = db.Column(db.Float(4, 2), comment='提前赎回利率')
    pDeadline = db.Column(db.Integer, comment='选择期限')
    aCurrentPeriod = db.Column(db.Integer, comment='当前期（账户资金日志表）')
    pProspectiveEarnings = db.Column(db.Float(8, 2), comment='预期收益')
    pExpectedAnnualIncome = db.Column(db.Float(4, 2), comment='预期年化收益')
    pMonthInterest = db.Column(db.Float(8, 2), comment='每月盈取利息')
    pMonthlyExtractInterest = db.Column(db.Float(8, 2), comment='每月提取利息')
    pInterestStartDate = db.Column(db.DateTime, comment='开始计息时间')
    pInterestEndDate = db.Column(db.Integer, comment='结束计息时间')
    pEarningsIsFinished = db.Column(db.Float(10, 2), comment='收益是否完成')
    pAvailableBalance = db.Column(db.Float(10, 2), comment='可用余额')
    pFrozenMoney = db.Column(db.Float(10, 2), comment='冻结金额')
    pSystemPaymentDate = db.Column(db.Integer, comment='每月回款日')
    pCurrentMonth = db.Column(db.Integer, comment='当前期（用户购买产品记录表）')
    pDeductInterest = db.Column(db.Float(8, 2), comment='扣去利息')
    pNotInvestMoney = db.Column(db.Float(10, 2), comment='未投资金额')
    pStatus = db.Column(db.Integer, comment='状态')  # 1 表是正式产生收益了 ，2收益结束，投资结束
    pEndInvestTotalMoney = db.Column(db.Float(8, 2), comment='到期应回总本息')
    pCurrentRealTotalMoney = db.Column(db.Float(8, 2), comment='当前期实回总本息')
    pDeadlineCount = db.Column(db.Float(8, 2), comment='统计')
    pProductName = db.Column(db.String(32), comment='产品名称')
    pMonthlyDeposit = db.Column(db.Float(8, 2), comment='月存')
    pMonthlyDepositCount = db.Column(db.Integer, comment='月存笔数')
    pTakeMonth = db.Column(db.Float(8, 2), comment='月乘')
    pTakeMonthCount = db.Column(db.Integer, comment='月乘笔数')
    pMayTake = db.Column(db.Float(8, 2), comment='月取')
    pMayTakeCount = db.Column(db.Integer, comment='月取笔数')
    pTotalAsDay = db.Column(db.Integer, comment='总天数')
    pDeadlineAsDay = db.Column(db.Integer, comment='投资天数')
    pDays = db.Column(db.Integer, comment='天数')
    pDeadlines = db.Column(db.DateTime, comment='投资期限')
    username = db.Column(db.String(64), comment='投资用户名')
    pEarnedInterest = db.Column(db.Float(8, 2), comment='已赚取利息')
    pRemark = db.Column(db.String(64), comment='备注')
    sumAvailableBalanceAndFrozenMoney = db.Column(db.Float(8, 2), comment='SUM(可用余额+冻结金额)')
    pTotal = db.Column(db.Float(8, 2), comment='总计')


class Deal_Record(db.Model):
    __tablename__ = 'deal_record'
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True, comment='主键')
    aUserId = db.Column(db.BIGINT, ForeignKey('user.id'), comment='用户id')
    user = db.relationship('User', backref=db.backref('deal_record', lazy=True))
    pId = db.Column(db.BIGINT, ForeignKey('invest_record.id'), comment='投资记录主键')
    invest_record = db.relationship('Invest_Record', backref=db.backref('deal_record', lazy=True))
    aCurrentPeriod = db.Column(db.Integer, comment='当前期')
    aReceiveOrPay = db.Column(db.Integer, comment='收付,1表示收，0表示付款')
    aTransferSerialNo = db.Column(db.String(128), comment='交易流水号')
    aDate = db.Column(db.DateTime, default=datetime.now(), comment='交易时间')
    aType = db.Column(db.Integer, comment='交易类型', default=0)
    aTransferStatus = db.Column(db.Integer, comment='交易状态，0代表失败，1代表交易成功', default=0)
    aBeforeTradingMoney = db.Column(db.Float(8, 2), comment='交易前金额', default=0)
    aAmount = db.Column(db.Float(8, 2), comment='金额', default=0)
    aAfterTradingMoney = db.Column(db.Float(8, 2), comment='交易后金额', default=0)
    aDescription = db.Column(db.String(128), comment='交易详情')