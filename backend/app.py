from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from models import db
from routes import register_routes
from config import Config
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ims.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'

# Initialize extensions
db.init_app(app)  # Ensure this is done before any db calls
jwt = JWTManager(app)
api = Api(app, prefix='/api')
CORS(app)

# JWT Unauthorized Handler
@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({'message': 'Missing or invalid token'}), 401

# Register routes
register_routes(api)

# Initialize database within app context
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
