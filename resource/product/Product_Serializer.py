from utils.Serializer import ListSerializer


class ProductSerializer(ListSerializer):
    def to_dict(self):
        products = []
        for product in self.data_list:
            products.append({
                'id': product.proId,
                'productNum': product.proNum,
                'productName': product.productName,
                'minLimit': product.lowerTimeLimit,
                'maxLimit': product.upperTimeLimit,
                'earning': '年利率' if product.earningType == 134 else '月利率',
                'returnMoney': '一次性回款' if product.wayToReturnMoney == 110 else '每月部分回款',
                'closedPeriod': product.closedPeriod,
                'status': product.status,
                'proLowerInvest': product.proLowerInvest
            })
        return products


class ProductRateSerializer(ListSerializer):
    def to_dict(self):
        rates = []
        for rate in self.data_list:
            rates.append({
                'id': rate.id,
                'productId': rate.productId,
                'month': rate.month,
                'incomeRate': float(rate.incomeRate)
            })
        return rates