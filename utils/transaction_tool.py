import random
from datetime import datetime


def generate_transaction_id(deal_type, date=None):
    if not date:
        date = datetime.now().strftime('%Y%m%d')
    return f'{deal_type}{random.randint(1000, 9999)}{date}'


if __name__ == '__main__':
    print(generate_transaction_id(123))
