from utils.Serializer import BaseSerializer, ListSerializer


class UserInfoSerializer(BaseSerializer):
    def to_dict(self):
        user = self.data
        return {
            'id': user.username,
            "realNameAuth": user.realNameStatus,
            "phoneStatus": user.phone,
            'loginStatus': 1,
            "payPwdStatus": user.payPwdStatus,
            'avatar': user.avatar,
            'inviteId': user.inviteId,
            'phone': user.phone
        }


class AccountSerializer(BaseSerializer):
    def to_dict(self):
        account = self.data
        return {
            'total': float(account.total),  # 账户总额
            "balance": float(account.balance),  # 账户可用余额
            "profit": float(account.interestA),  # 已投资总额
            "investmentW": float(account.investmentW),  # 总计待收本金
            "interestTotal": float(account.interestTotal),  # 总计待收利息
            'discount': float(account.discount)  # 代金券
        }


class BankcardSerializer(ListSerializer):
    def to_dict(self):
        bankcards = []
        for bankcard in self.data_list:
            bankcards.append(
                {
                    'id': bankcard.id,
                    'bankCardNum': bankcard.bankCardNum,
                    'openingBank': bankcard.openingBank
                }
            )
        return bankcards


class InviteListSerializer(ListSerializer):
    def to_dict(self):
        l = []
        for obj in self.data_list:
            l.append(
                {
                    'name': obj.username,
                    'registerTime': obj.registerTime.strftime("%Y-%m-%d"),
                    "award": 'coupon 50',
                }
            )
        return l
