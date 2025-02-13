from functools import wraps
from flask import request, Response
import os
from werkzeug.security import generate_password_hash, check_password_hash

def check_auth(username, password):
    """Kullanıcı adı ve şifreyi kontrol et"""
    stored_username = os.getenv('ADMIN_USERNAME')
    stored_password_hash = os.getenv('ADMIN_PASSWORD_HASH')
    return username == stored_username and check_password_hash(stored_password_hash, password)

def authenticate():
    """Return 401 response"""
    return Response(
        'Login required to view this page.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated 