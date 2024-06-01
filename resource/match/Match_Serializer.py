from utils.Serializer import PaginatorSerializer
from datetime import datetime


class MatchPaginatorSerializer(PaginatorSerializer):
    def get_obj(self, obj):
        return {
            'weigh': 0,
            'username': obj.invest_record.user.username,
            "invest_recordNum": obj.invest_record.pSerialNo,
            "productName": obj.invest_record.product.productName,
            'investDate': obj.invest_record.pDate.strftime("%Y-%m-%d"),
            'period': obj.invest_record.pDeadlineAsDay,
            'notMatchedMoney': float(obj.NotMatchedMoney),
            'matchStatus': obj.matchedStatus,
        }


class ExpectedReturnPaginatorSerializer(PaginatorSerializer):
    def get_obj(self, obj):
        return {
            'return_id': obj.id,
            'userId': obj.userId,
            'productId': obj.product.productName,
            "investRcordID": obj.invest_record,
            "expectedDate": obj.expectedDate.strftime("%Y-%m-%d"),
            'expectedStamp': datetime.timestamp(datetime(obj.expectedDate.date().year, obj.expectedDate.date().month,
                                                         obj.expectedDate.date().day)),
            'return_Money': float(obj.expectedMoney),

        }


class MatchedResultPaginatorSerializer(PaginatorSerializer):
    def get_obj(self, obj):
        return {
            'userId': obj.userId,
            'debtId': obj.debtId,
            "investId": obj.investId,
            "transNo": obj.transferSerialNo,
            'Money': float(obj.purchaseMoney),
            'matchDate': obj.matchDate.strftime("%Y-%m-%d %H:%M:%S")
        }
