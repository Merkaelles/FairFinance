from decimal import Decimal

from dateutil.relativedelta import relativedelta
from flask import g, current_app
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from models import db
from models.user import User
from models.loan_repay import Loan, DebtInfo, Repay
from resource import const
from resource.loan.Loan_Serializer import *
from utils.cache_redis import redis_cli
from utils.transaction_tool import generate_transaction_id
from utils.decorators import login_required
from datetime import datetime


class Loan_Apply(Resource):
    method_decorators = [login_required]

    def post(self):
        rp = RequestParser()
        rp.add_argument('amount', required=True)
        rp.add_argument('auth_code', required=True)
        rp.add_argument('loanMonth', required=True)
        args = rp.parse_args()
        amount = args.amount
        loan_month = args.loanMonth
        auth_code = args.auth_code
        user_id = g.user_id
        u = User.query.filter(User.id == user_id).first()
        try:
            auth_code_x = redis_cli.get(f'auth code to {u.phone}').decode()
            if not auth_code_x:
                current_app.logger.info('The auth code expired')
                return {'message': 'The auth code expired', 'code': 201}
            elif auth_code != auth_code_x:
                current_app.logger.info('The auth code is wrong')
                return {'message': 'The auth code is wrong', 'code': 201}
        except ConnectionError as e:
            current_app.logger.error(e)
            return {'message': 'Redis connection failed', 'code': 201}
        loan = Loan(loanAmount=amount, lUid=user_id, duration=loan_month, lName=u.username,
                    lRate=const.LoanConfig.YEAR_RATE.value,
                    lRepayDay=datetime.now().day)
        db.session.add(loan)
        db.session.commit()
        return {'msg': 'OK'}

    def get(self):
        rp = RequestParser()
        rp.add_argument('start')
        rp.add_argument('end')
        rp.add_argument('page')
        rp.add_argument('per_page')
        rp.add_argument('approve_status')
        args = rp.parse_args()
        start = args.get('start')
        end = args.get('end')
        page = int(args.get('page'))
        per_page = int(args.get('per_page'))
        status = int(args.get('approve_status'))
        if status > 0:
            loan_list = Loan.query.filter(Loan.status > 0)
        else:
            loan_list = Loan.query.filter(Loan.status == status)

        if start and end:
            loan_list = loan_list.filter(db.cast(Loan.applyDate, db.DATE) >= db.cast(start, db.DATE)) \
                .filter(db.cast(Loan.applyDate, db.DATE) <= db.cast(end, db.DATE)) \
                .paginate(page=page, per_page=per_page, error_out=False)
        else:
            loan_list = loan_list.paginate(page=page, per_page=per_page, error_out=False)

        loan_data = LoanPaginatorSerializer(loan_list).to_dict()

        return {'msg': 'OK', 'loan_data': loan_data}

    def put(self):
        rp = RequestParser()
        rp.add_argument('applyId')
        rp.add_argument('status')
        args = rp.parse_args()
        loan_id = args.get('applyId')
        status = args.get('status')
        loan = Loan.query.filter(Loan.id == loan_id).first()
        loan.status = int(status)

        if status == '1':
            debt_no = generate_transaction_id('debt')
            debtors_id = loan.user.idNum  # 身份证号码
            end_date = datetime.now() + relativedelta(months=loan.duration)
            new_debt = DebtInfo(debtNo=debt_no, debtorsName=loan.lName, loanNo=loan.id, borrowerId=loan.lUid,
                                debtorsId=debtors_id, loanStartDate=datetime.now(), loanPeriod=loan.duration,
                                loanEndDate=end_date, repaymentStyleName=loan.lRepayType, matchedMoney=0,
                                repayDate=loan.lRepayDay, repayMoney=loan.loanAmount, matchedStatus=0,
                                debtMoney=loan.loanAmount, debtYearRate=loan.lRate, debtTransferMoney=0)
            db.session.add(new_debt)
            db.session.flush()
            self.create_repay_plan(new_debt)
        db.session.commit()
        return {'msg': 'OK'}

    def create_repay_plan(self, new_debt):
        amount_cost = round(new_debt.repayMoney / new_debt.loanPeriod, 2)
        amount_rate = round(const.LoanConfig.YEAR_RATE.value / 12, 4)
        for m in range(1, new_debt.loanPeriod + 1):
            interest = round((new_debt.repayMoney - amount_cost * (m - 1)) * Decimal(amount_rate), 2)
            total = float(round(interest + amount_cost, 2))
            repay_plan = Repay(claimsId=new_debt.id, receivableMoney=total,
                               currentTerm=m, recordDate=datetime.now())
            db.session.add(repay_plan)


class MyLoan(Resource):
    def get(self):
        rp = RequestParser()
        rp.add_argument('page')
        rp.add_argument('per_page')
        args = rp.parse_args()
        page = int(args.get('page'))
        per_page = int(args.get('per_page'))
        loan_list = Loan.query.filter(Loan.lUid == g.user_id).paginate(page=page, per_page=per_page, error_out=False)
        loan_data = LoanPaginatorSerializer(loan_list).to_dict()

        return {'msg': 'OK', 'loan_data': loan_data}


class Debt(Resource):

    def get(self):
        rp = RequestParser()
        rp.add_argument('start')
        rp.add_argument('end')
        rp.add_argument('curPage')
        rp.add_argument('perPage')
        args = rp.parse_args()
        start = args.get('start')
        end = args.get('end')
        cur_page = int(args.get('curPage'))
        per_page = int(args.get('perPage'))
        debt_list = DebtInfo.query
        if start and end:
            debt_list = debt_list.filter(db.cast(DebtInfo.loanStartDate, db.DATE) >= db.cast(start, db.DATE)) \
                .filter(db.cast(DebtInfo.loanStartDate, db.DATE) <= db.cast(end, db.DATE)) \
                .paginate(page=cur_page, per_page=per_page, error_out=False)
        else:
            debt_list = debt_list.paginate(page=cur_page, per_page=per_page, error_out=False)

        debt_data = DebtPaginatorSerializer(debt_list).to_dict()

        return {'msg': 'OK', 'debt_data': debt_data}


class Repayment(Resource):
    method_decorators = [login_required]

    def get(self):
        rp = RequestParser()
        rp.add_argument('claimsId')
        args = rp.parse_args()
        claimsId = args.claimsId
        repayments = Repay.query.filter(Repay.claimsId == claimsId).all()
        if repayments:
            repay_data = RepayPlanSerializer(repayments).to_dict()
            return {'msg': 'OK', 'repay_data': repay_data}
        return {'message': 'No repayments to deal with', 'code': 201}

    def post(self):
        rp = RequestParser()
        rp.add_argument('repay_id')
        rp.add_argument('repayAmount')
        args = rp.parse_args()
        repay_id = int(args.get('repay_id'))
        repay_money = float(args.get('repayAmount'))
        u = User.query.filter(User.id == g.user_id).first()
        if u.account.balance < repay_money:
            return {'message': '可用余额不足', 'code': 205}
        else:
            u.account.balance = float(u.account.balance) - repay_money
            repay = Repay.query.filter(Repay.id == repay_id).first()
            repay.isReturned = 1
            repay.recordDate = datetime.now()
            db.session.commit()
            return {'msg': 'Repay finished'}