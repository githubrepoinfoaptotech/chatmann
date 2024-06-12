from flask import Blueprint, request,jsonify, make_response,session
from services.enquiry_services import enquiry,getAllEnquiry
enquiry_route = Blueprint('enquiry_route', __name__)
from utils.JwtToken import validate_token_admin,validate_apiKey

@enquiry_route.route('/api/v1/enquiry/addenquiry', methods=['GET', 'POST'])
@validate_apiKey
def Myenquiry():
    data = request.get_json()
    return enquiry(data)
@enquiry_route.route("/api/v1/enquiry/getAllEnquiry", methods=['POST'])
@validate_token_admin
def get_all_enquiry():
    data = request.get_json()
    return getAllEnquiry(data)