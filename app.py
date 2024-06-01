from create_app import create_app
from settings import Development, Production
from models.user import User, Account, Bankcard
from models.message import Message, Message_Content
from models.product import Product, Product_Rate, Expected_Return
from models.record import Invest_Record, Deal_Record
from models.loan_repay import Loan, DebtInfo, Repay
from models.match import Funding_not_matched, Matched_Result

app = create_app(Development)


@app.route('/')
def hi():
    return f"Keep going , you're one step from success !"


if __name__ == '__main__':
    app.run()
