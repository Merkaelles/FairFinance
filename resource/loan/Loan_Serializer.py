from utils.Serializer import *


class LoanPaginatorSerializer(PaginatorSerializer):
    def get_obj(self, obj):
        return {
            'loanId': obj.id,
            'name': obj.lName,
            "applyTime": obj.applyDate.strftime("%Y-%m-%d %H:%M:%S"),
            "amount": float(obj.loanAmount),
            'duration': obj.duration,
            'loanRate': float(obj.lRate),
            'repayDay': obj.lRepayDay,
            'repayType': obj.lRepayType,
            'status': obj.status,
            'debt_match_status': obj.debt_info.matchedStatus if obj.debt_info else '',
            'debt_id': obj.debt_info.id if obj.debt_info else '',

        }


class DebtPaginatorSerializer(PaginatorSerializer):
    def get_obj(self, obj):
        return {
            'debtNo': obj.debtNo,
            'loanNo': obj.loanNo,
            "loanStartDate": obj.loanStartDate.strftime("%Y-%m-%d"),
            "repayDate": obj.repayDate,
            'debtYearRate': float(obj.debtYearRate),
            'debtMoney': float(obj.debtMoney),
            'debtOriginalMoney': float(obj.repayMoney),
            'matchedStatus': obj.matchedStatus,
            'matchedMoney': float(obj.matchedMoney),
            'debtStatus': obj.matchedStatus,
        }


class RepayPlanSerializer(ListSerializer):
    def to_dict(self):
        Repayments = []
        for obj in self.data_list:
            Repayments.append(
                {
                    'id': obj.id,
                    'currentTerm': obj.currentTerm,
                    'receivableDate': obj.receivableDate.strftime("%Y-%m-%d"),
                    "receivableMoney": float(obj.receivableMoney),
                    'isReturned': obj.isReturned,
                }
            )
        return Repayments
