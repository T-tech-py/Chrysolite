from flask import Blueprint

user = Blueprint("user",url_prefix='/user')

@user.route('/user/auth/signup')
def signup():
    return ""