from flask import Blueprint, request
from services.payment_service import initiate_transaction,view_all_plans,get_PaymentSuccess,view_all_transactions,view_transaction
payment_route = Blueprint('payment_route', __name__)
from utils.JwtToken import validate_token_admin
from utils.functions import setCountryCode

@payment_route.route("/api/v1/payment/initiateTransaction", methods=['POST'])
@validate_token_admin
def initiateTransaction():
    data = request.get_json()
    return initiate_transaction(data)
@payment_route.route("/api/v1/payment/viewAllPlans", methods=['POST'])
def viewAllPlans():
    setCountryCode()
    return view_all_plans()
@payment_route.route("/api/v1/payment/getPaymentSuccess", methods=['POST'])
@validate_token_admin
def getPaymentSuccess():
    data = request.get_json()
    return get_PaymentSuccess(data)
@payment_route.route("/api/v1/payment/viewAllTransactions", methods=['POST'])
@validate_token_admin
def viewAllTransactions():
    data = request.get_json()
    return view_all_transactions(data)
@payment_route.route("/api/v1/payment/viewTransaction", methods=['POST'])
@validate_token_admin
def viewTransaction():
    data = request.get_json()
    return view_transaction(data)
