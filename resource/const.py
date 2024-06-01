import os
from enum import Enum

LIMIT_SMS_CODE_BY_PHONE = '5/minute'
LIMIT_SMS_CODE_BY_IP = '60/h'
SMS_VERIFY_CODE_EXPIRE = 5 * 60

INVITE_BONUS = 50

JWT_EXPIRE_TIME = 24 * 60 * 60
SECRET_KEY = os.urandom(16)


class DealType(Enum):
    all = 0  # 全部类型
    recharge = 1  # 充值
    extract = 2  # 提现
    invest = 3  # 投资
    income = 4  # 收益
    recycle = 5  # 回收本金
    match = 6  # 匹配结果


class LoanConfig(Enum):
    YEAR_RATE = 0.055  # 年利率
