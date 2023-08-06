from flask import jsonify,request
from functools import wraps
from solution_efe_client_security.securityService import securityServiceTokenValid

def guardSecurity(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is Missing'}), 401
        try:
            headers = token.split()
            if (len(headers) != 2):
                return jsonify({'message': 'Token is Missing'}), 401
            data = securityServiceTokenValid(headers[1])
            if(not data['status']):
                return jsonify({'message': 'Token is Invalid'}), 401
        except:
            return jsonify({'message': 'Token is Invalid'}), 401
        return f(*args, **kwargs)
    return decorated
    