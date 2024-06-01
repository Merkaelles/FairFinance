import decimal
import string
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
import uuid
import random
from resource.const import DealType

a = {'id': 1231}
print(a.get('b'))
# print(a['c'])
r = ''.join(random.sample(string.digits + string.ascii_uppercase, 5))
a.update({'b': 12, 'r': 14})
print(a)
print(type(random.randint(100, 999)))
print(DealType.invest.name)
print(datetime.now() + relativedelta(months=12))
print(uuid.uuid3(uuid.NAMESPACE_DNS, '花木兰'))
print(uuid.uuid5(uuid.NAMESPACE_DNS, '花木兰'))
print('ids' in a)
a=3.2
print(type(a), a)
print(type(decimal.Decimal(a)), decimal.Decimal(a))