from utils.Serializer import PaginatorSerializer


class InvestRecordSerializer(PaginatorSerializer):
    def get_obj(self, obj):
        return {
            'id': obj.id,
            'plan_name': obj.product.productName,
            'invest_amount': float(obj.pAmount),
            "yearRate": float(obj.pEarnings),
            "totalIncome": float(obj.pMonthlyExtractInterest * obj.pDeadline),
            'month_Income': float(obj.pMonthlyExtractInterest),
            'deal_date': obj.pBeginDate.strftime("%Y-%m-%d"),
            'period': obj.pDeadline,
            'status': obj.pStatus,
            'remark': obj.pRemark
        }


class DealRecordSerializer(PaginatorSerializer):
    def get_obj(self, obj):
        return {
            'deal_date': obj.aDate.strftime("%Y-%m-%d"),
            'deal_type': obj.aType,
            "description": obj.aDescription,
            "deal_amount": float(obj.aAmount),
            'aAfter_Money': float(obj.aAfterTradingMoney),
            'deal_status': '交易成功' if obj.aTransferStatus else '交易失败',
            'user_name': obj.user.username
        }
