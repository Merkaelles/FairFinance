from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import g, current_app
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from models.match import Funding_not_matched
from models.user import User, Account
from models.product import Product, Product_Rate
from models.record import Invest_Record, Deal_Record
from models import db
from resource.product.Product_Serializer import ProductSerializer, ProductRateSerializer
from resource.product.Record_Serializer import InvestRecordSerializer, DealRecordSerializer
from utils.transaction_tool import generate_transaction_id
from resource import const


class Product_Display(Resource):
    def get(self):
        products = Product.query.all()
        product_data = ProductSerializer(products).to_dict()
        return {'msg': 'OK', 'product_data': product_data}


class ProductRate_Query(Resource):
    def get(self):
        rp = RequestParser()
        rp.add_argument('productId', required=True, location='args')
        args = rp.parse_args()
        productId = args.productId
        rate_list = Product_Rate.query.filter(Product_Rate.productId == productId).all()
        product_rate_data = ProductRateSerializer(rate_list).to_dict()
        return {'msg': 'OK', 'product_rate_data': product_rate_data}


def interest(rate, amount):
    return round(amount / 12 * rate / 100, 2)


class Invest(Resource):
    def get(self):
        rp = RequestParser()
        rp.add_argument('start', location='args')
        rp.add_argument('end', location='args')
        rp.add_argument('invest_type', location='args')
        rp.add_argument('page', location='args')
        rp.add_argument('per_page', location='args')
        args = rp.parse_args()
        start = args.get('start')
        end = args.get('end')
        invest_type = 0 if args.get('invest_type') is None else int(args.get('invest_type'))
        page = int(args.get('page'))
        per_page = int(args.get('per_page'))
        q = Invest_Record.query.filter(Invest_Record.pUid == g.user_id, Invest_Record.pStatus == invest_type)
        if start and end:
            q = q.filter(db.cast(Invest_Record, db.DATE) >= db.cast(start, db.DATE),
                         db.cast(Invest_Record, db.DATE) <= db.cast(end, db.DATE))
        invest_paginator = q.paginate(page, per_page, error_out=False)
        invest_data = InvestRecordSerializer(invest_paginator).to_dict()
        return {'msg': 'OK', 'invest_data': invest_data}

    def post(self):
        rp = RequestParser()
        rp.add_argument('productId', required=True, location='form')
        rp.add_argument('pAmount', required=True, location='form')
        rp.add_argument('period', required=True, location='form')
        args = rp.parse_args()
        proId = args.productId
        pAmount = float(args.pAmount)
        period = int(args.period)
        u = User.query.filter(User.id == g.user_id).first()
        product = Product.query.filter(Product.proId == proId).first()
        rate = Product_Rate.query.filter(Product_Rate.productId == proId, Product_Rate.month == period).first()
        income = interest(float(rate.incomeRate), pAmount)
        try:
            account_query = Account.query.filter(Account.userId == g.user_id)
            account = account_query.first()
            discount = 50 if account.discount >= 50 else 0
            realPay = pAmount - discount
            if account.balance >= realPay:
                before_balance = account.balance
                now_balance = float(account.balance) - realPay
                now_discount = account.discount - discount

            else:
                return {'message': 'Available balance not enough', 'code': 201}
            interestTotal = income * period
            account_query.update({
                'balance': now_balance,
                'investmentA': float(account.investmentA) + pAmount,
                'investmentW': float(account.investmentW) + pAmount,
                'frozen': float(account.frozen) + realPay,
                'interestTotal': float(account.interestTotal) + interestTotal,
                'discount': now_discount
            })
            invest_id = generate_transaction_id(const.DealType.invest.name)
            remark = "使用了50元的代金券。" if discount == 50 else '没有使用代金券'
            p_end_date = datetime.now() + relativedelta(months=period)
            invest_days = (p_end_date - datetime.now()).days
            invest_record = Invest_Record(id=proId, pUid=g.user_id, pBeginDate=datetime.now(),
                                          pEndDate=p_end_date, pSerialNo=invest_id, pAmount=pAmount,
                                          pEarnings=rate.incomeRate, pDeadline=period, pMonthInterest=income,
                                          pMonthlyExtractInterest=income, pAvailableBalance=u.account.balance,
                                          pFrozenMoney=realPay, pProductName=product.productName,
                                          pDeadlineAsDay=invest_days, username=u.username,
                                          pProspectiveEarnings=interestTotal, pStatus=0, pRemark=remark)
            db.session.add(invest_record)
            db.session.flush()
            not_matched = Funding_not_matched(InvestRecordId=invest_record.id, NotMatchedMoney=pAmount,
                                              FundsWeight=1, matchedStatus=0)
            db.session.add(not_matched)
            deal_num = generate_transaction_id(const.DealType.invest.name)
            deal_record = Deal_Record(aUserId=g.user_id, pId=invest_record.id, aReceiveOrPay=1,
                                      aTransferSerialNo=deal_num,
                                      aTransferStatus=1, aBeforeTradingMoney=before_balance, aAmount=pAmount,
                                      aAfterTradingMoney=now_balance, aDescription='投资产品购买',
                                      aType=const.DealType.invest.value)
            db.session.add(deal_record)
            db.session.commit()
            return {'msg': 'invest finished'}
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return {'message': 'Service Busy'}, 500


class Deal(Resource):
    def get(self):
        rp = RequestParser()
        rp.add_argument('start', location='args')
        rp.add_argument('end', location='args')
        rp.add_argument('deal_type', location='args')
        rp.add_argument('page', required=True, location='args')
        rp.add_argument('per_page', required=True, location='args')
        args = rp.parse_args()
        start = args.get('start')
        end = args.get('end')
        deal_type = 0 if args.get('deal_type') is None else int(args.get('deal_type'))
        page = int(args.get('page'))
        per_page = int(args.get('per_page'))
        user_id = g.user_id
        user = User.query.filter(User.id == user_id).first()
        q = Deal_Record.query
        if deal_type > 0:
            q = q.filter(Deal_Record.aType == deal_type)
        if user.role == 0:
            q = q.filter(Deal_Record.aUserId == user_id)
        if start and end:
            q = q.filter(db.cast(Deal_Record.aDate, db.DATE) >= db.cast(start, db.DATE)) \
                .filter(db.cast(Deal_Record.aDate, db.DATE) <= db.cast(end, db.DATE))
        data_query = q.paginate(page=page, per_page=per_page, error_out=False)
        deal_data = DealRecordSerializer(data_query).to_dict()

        return {'msg': 'OK', 'deal_data': deal_data}
