from collections import deque
from dateutil.relativedelta import relativedelta
from flask import g, current_app
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy import or_
from models import db
from models.record import Invest_Record, Deal_Record
from models.user import Account
from models.product import Expected_Return
from models.loan_repay import DebtInfo
from models.match import Funding_not_matched, Matched_Result
from resource import const
from .Match_Serializer import *
from utils.transaction_tool import generate_transaction_id
from utils.decorators import login_required


class MatchDeque:
    def __init__(self, item_list):
        self.items = deque(item_list)  # deque 双端队列

    def get_item(self):
        return self.items.popleft()

    def push(self, item):
        return self.items.appendleft(item)

    @property
    def isEmpty(self):
        return len(self.items) == 0


class Match:
    def __init__(self):
        debts = DebtInfo.query.filter(or_(DebtInfo.matchedStatus == 0, DebtInfo.matchedStatus == 1)).order_by(
            DebtInfo.debtMoney).all()
        self.debt_deque = MatchDeque(debts)

        funds = Funding_not_matched.query.filter(
            or_(Funding_not_matched.matchedStatus == 0, Funding_not_matched.matchedStatus == 1)).order_by(
            Funding_not_matched.NotMatchedMoney).all()
        self.fund_deque = MatchDeque(funds)

    def start_match(self):
        try:
            while (not self.debt_deque.isEmpty) and (not self.fund_deque.isEmpty):
                debt = self.debt_deque.get_item()
                fund = self.fund_deque.get_item()
                if debt.debtMoney > fund.NotMatchedMoney:
                    self.debt_gt_fund(debt, fund)
                elif debt.debtMoney < fund.NotMatchedMoney:
                    self.debt_lt_fund(debt, fund)
                else:
                    self.debt_eq_fund(debt, fund)
            db.session.commit()
            return {'msg': '债务与资金匹配完成'}
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return {'message': '服务器繁忙，请稍后重试'}, 500

    def debt_gt_fund(self, debt, fund):
        self.make_match_result(debt, fund, fund.NotMatchedMoney)
        debt.debtMoney -= fund.NotMatchedMoney
        debt.matchedStatus = 1
        debt.matchedMoney += fund.NotMatchedMoney
        fund.NotMatchedMoney = 0
        fund.matchedStatus = 2
        self.debt_deque.push(debt)
        self.make_expected_return(fund)

    def debt_lt_fund(self, debt, fund):
        fund.NotMatchedMoney -= debt.debtMoney
        fund.matchedStatus = 1
        self.make_match_result(debt, fund, debt.debtMoney)
        debt.matchedMoney += debt.debtMoney
        debt.debtMoney = 0
        debt.user.account.balance += debt.repayMoney
        debt.matchedStatus = 2
        self.start_repay(debt)
        self.fund_deque.push(fund)

    def debt_eq_fund(self, debt, fund):
        debt.matchedStatus = 2
        debt.matchedMoney += debt.debtMoney
        self.make_match_result(debt, fund, debt.debtMoney)
        debt.debtMoney = 0
        fund.NotMatchedMoney = 0
        fund.matchedStatus = 2
        self.make_expected_return(fund)
        self.start_repay(debt)

    def make_match_result(self, debt, fund, match_money):
        match_id = generate_transaction_id(const.DealType.match.name)
        match_result = Matched_Result(userId=fund.invest_record.pUid, debtId=debt.id, investId=fund.invest_record.id,
                                      transferSerialNo=match_id, purchaseMoney=match_money,
                                      confirmedDate=fund.invest_record.pDate,
                                      isConfirmed=1, matchDate=datetime.now())
        db.session.add(match_result)

    def make_expected_return(self, fund):
        expect_return = Expected_Return(userId=fund.invest_record.pUid, productId=fund.invest_record.pProductId,
                                        investRecord=fund.invest_record.id,
                                        expectedDate=datetime.now() + relativedelta(
                                            months=fund.invest_record.pDeadline),
                                        expectedMoney=fund.invest_record.pProspectiveEarnings)
        fund.invest_record.pStatus = 1
        fund.invest_record.pInterestStartDate = datetime.now()
        db.session.add(expect_return)

    def start_repay(self, debt):
        repay_list = debt.repay
        for i in range(len(repay_list)):
            repay_date = datetime.now() + relativedelta(months=(i + 1))
            repay_list[i].receivableDate = repay_date


class Matching(Resource):
    def post(self):
        match = Match()
        return match.start_match()


class Matches(Resource):
    def get(self):
        rp = RequestParser()
        rp.add_argument('page', location='args')
        rp.add_argument('per_page', location='args')
        rp.add_argument('status', location='args')
        args = rp.parse_args()
        page = int(args.get('page'))
        per_page = int(args.get('per_page'))
        status = int(args.get('status'))
        if status == 2:
            matched_list = Funding_not_matched.query.filter(Funding_not_matched.matchedStatus == 2)
        else:
            matched_list = Funding_not_matched.query.filter(Funding_not_matched.matchedStatus != 2)
        matched_list = matched_list.paginate(page=page, per_page=per_page, error_out=False)
        match_data = MatchPaginatorSerializer(matched_list).to_dict()

        return {'msg': 'success', 'match_data': match_data}


class Returns(Resource):
    def get(self):
        rp = RequestParser()
        rp.add_argument('curPage', location='args')
        rp.add_argument('perPage', location='args')
        args = rp.parse_args()
        cur_page = int(args.get('curPage'))
        per_page = int(args.get('perPage'))
        return_list = Expected_Return.query.filter(Expected_Return.userId == g.user_id)
        return_list = return_list.paginate(page=cur_page, per_page=per_page, error_out=False)
        returns_data = ExpectedReturnPaginatorSerializer(return_list).to_dict()
        return {'msg': 'success', 'returns_data': returns_data}


class MatchedResults(Resource):
    def get(self):
        rp = RequestParser()
        rp.add_argument('start', location='args')
        rp.add_argument('end', location='args')
        rp.add_argument('curPage', location='args')
        rp.add_argument('perPage', location='args')
        args = rp.parse_args()
        cur_page = int(args.get('curPage'))
        per_page = int(args.get('perPage'))
        start = args.get('start')
        end = args.get('end')
        query = Matched_Result.query
        if start and end:
            query = query.filter(db.cast(Matched_Result.matchDate, db.DATE) >= db.cast(start, db.DATE)) \
                .filter(db.cast(Matched_Result.matchDate, db.DATE) <= db.cast(end, db.DATE))
        result_list = query.paginate(page=cur_page, per_page=per_page, error_out=False)
        match_result_data = MatchedResultPaginatorSerializer(result_list).to_dict()
        return {'msg': 'success', 'match_result_data': match_result_data}


class Invest_Income(Resource):
    method_decorators = [login_required]

    def post(self):
        rp = RequestParser()
        rp.add_argument('return_id', location='form')
        args = rp.parse_args()
        return_id = int(args.get('return_id'))
        uid = g.user_id
        uid = 2
        account = Account.query.filter(Account.userId == uid).first()
        expected_income = Expected_Return.query.filter(Expected_Return.id == return_id).first()

        if expected_income:
            cur_date = datetime.now().date()
            expected_date = expected_income.expectedDate.date()
            if cur_date >= expected_date:
                try:
                    invest = Invest_Record.query.filter(Invest_Record.id == expected_income.investRecord).first()
                    invest.pStatus = 2
                    account.interestA += expected_income.expectedMoney
                    account.interestTotal -= expected_income.expectedMoney
                    account.investmentW -= invest.pAmount
                    account.frozen -= invest.pAmount
                    before_balance = account.balance
                    account.balance += (invest.pAmount + expected_income.expectedMoney)
                    account.total += expected_income.expectedMoney
                    del_num = generate_transaction_id(const.DealType.income)
                    deal_log = Deal_Record(aUserId=uid, aReceiveOrPay=1, aTransferSerialNo=del_num,
                                           aTransferStatus=1, aBeforeTradingMoney=before_balance,
                                           aAmount=expected_income.expectedMoney, aAfterTradingMoney=account.balance,
                                           aDescreption='提取收益', aType=const.DealType.income.value)
                    expected_income.expectedMoney = 0
                    db.session.add(deal_log)
                    db.session.commit()
                    return {'msg': 'OK'}
                except Exception as e:
                    current_app.logger.error(e)
                    db.session.rollback()
                    return {'message': '系统出错'}, 500
            else:
                return {'message': '投资未到期 income not up to date', 'code': 201}
        else:
            return {'message': '没有找到的该预期首页'}, 401
