from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from db import db
from blacklist import BLACKLIST

from resources.item import Items, Item
from resources.user import UserRegister, User, UserLogin, TokenRefresh, UserLogout
from resources.store import Store, Stores

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_CHECKS'] = ['access', 'refresh']

api = Api(app)

jwt = JWTManager(app)


@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:
        return {'is_admin': True}
    return {'is_admin': False}


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_headers, jwt_payload):
    return jwt_payload['jti'] in BLACKLIST


@jwt.expired_token_loader
def expired_token_callback():
    return {'description': "The token has expired",
            'error': 'token_expired'}, 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'description': "Signification verification failed",
                    "error": "invalid_token"}), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "description": "Request does not contain an access token.",
        'error': 'authorization_required'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        "description": "The token is not fresh.",
        'error': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "description": "The token has been revoked.",
        'error': 'token_revoked'
    }), 401


@app.before_first_request
def create_tables():
    db.init_app(app=app)
    db.create_all()


api.add_resource(Items, '/items')
api.add_resource(Item, '/items/<string:name>')
api.add_resource(UserRegister, '/register')
api.add_resource(Store, '/stores/<string:name>')
api.add_resource(Stores, '/stores')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(UserLogout, '/logout')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
