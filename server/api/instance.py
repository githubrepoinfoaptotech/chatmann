from flask import Blueprint, request
from services.instance_service import add_instance,view_user_instance
instance_route = Blueprint('instance_route', __name__)
from utils.JwtToken import validate_token_admin

@instance_route.route("/api/v1/instance/addInstance", methods=['POST'])
@validate_token_admin
def addInstance():
    data = request.get_json()
    return add_instance(data)
@instance_route.route("/api/v1/instance/viewUserInstacne", methods=['POST'])
@validate_token_admin
def viewUserInstacne():
    data = request.get_json()
    return view_user_instance(data)