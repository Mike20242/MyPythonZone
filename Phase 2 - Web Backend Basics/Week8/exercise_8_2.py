# =====================================================================
# EXERCISE 8.2: LOGIN ENDPOINT (RETURN JWT TOKEN)
# =====================================================================
# Goal: Create a login endpoint that:
#   - Accepts username and password via JSON POST request
#   - Validates credentials against the database
#   - Returns a JWT (JSON Web Token) on successful login
#
# Key Concepts:
#   - JWT (JSON Web Tokens): A compact, URL-safe token format used for
#     authentication. It consists of three parts:
#       1. Header   - Algorithm and token type (e.g., HS256)
#       2. Payload  - Claims/data (e.g., user_id, expiration time)
#       3. Signature - Ensures the token hasn't been tampered with
#
#   - Token Flow:
#       Client sends credentials → Server verifies → Server returns JWT
#       Client stores JWT → Client sends JWT with future requests
#       Server verifies JWT → Server allows/denies access
#
# Dependencies: pip install flask sqlalchemy PyJWT werkzeug
# =====================================================================

import jwt
import datetime
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

# SECRET KEY for signing JWT tokens.
# In production, this should be stored in environment variables,
# NEVER hardcoded in source code!
app.config['SECRET_KEY'] = 'my-super-secret-key-change-in-production'

# Token expiration time (in minutes)
TOKEN_EXPIRATION_MINUTES = 30

# --- Database Setup ---
engine = create_engine('sqlite:///exercise_8_2.db', echo=False)
Base = declarative_base()


# --- User Model (same as Exercise 8.1) ---
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }

    def __repr__(self):
        return f"<User('{self.username}')>"


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# --- Error Handlers ---

@app.errorhandler(400)
def bad_request(error):
    message = error.description if hasattr(error, 'description') else "Bad request"
    return jsonify({"error": "Bad Request", "message": message}), 400

@app.errorhandler(401)
def unauthorized(error):
    message = error.description if hasattr(error, 'description') else "Unauthorized"
    return jsonify({"error": "Unauthorized", "message": message}), 401

@app.errorhandler(409)
def conflict(error):
    message = error.description if hasattr(error, 'description') else "Conflict"
    return jsonify({"error": "Conflict", "message": message}), 409


# --- Register Endpoint (from Exercise 8.1) ---

@app.route('/register', methods=['POST'])
def register():
    """POST /register - Create a new user account."""
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Invalid JSON format or missing Request Body.")

    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            raise BadRequest(f"Field '{field}' is required.")

    username = data['username']
    email = data['email']
    password = data['password']

    if not isinstance(username, str) or not username.strip():
        raise BadRequest("Field 'username' must be a non-empty string.")
    if not isinstance(email, str) or not email.strip():
        raise BadRequest("Field 'email' must be a non-empty string.")
    if not isinstance(password, str) or len(password) < 6:
        raise BadRequest("Field 'password' must be at least 6 characters.")

    username = username.strip()
    email = email.strip().lower()

    session = Session()
    try:
        if session.query(User).filter_by(username=username).first():
            return jsonify({"error": "Conflict", "message": "Username already exists."}), 409
        if session.query(User).filter_by(email=email).first():
            return jsonify({"error": "Conflict", "message": "Email already registered."}), 409

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        session.add(new_user)
        session.commit()

        return jsonify({
            "message": "User registered successfully",
            "user": new_user.to_dict()
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        session.close()


# --- Login Endpoint (NEW in Exercise 8.2) ---

@app.route('/login', methods=['POST'])
def login():
    """
    POST /login
    
    Authenticates a user and returns a JWT token.
    
    Request Body (JSON):
        {
            "username": "john_doe",
            "password": "securepassword123"
        }
    
    Success Response (200 OK):
        {
            "message": "Login successful",
            "token": "eyJhbGciOiJIUzI1NiIs...",
            "expires_in": "30 minutes"
        }
    
    Error Responses:
        400 - Missing fields
        401 - Invalid credentials
    """
    # 1. Parse and validate input
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Invalid JSON format or missing Request Body.")

    if 'username' not in data or 'password' not in data:
        raise BadRequest("Fields 'username' and 'password' are required.")

    username = data['username']
    password = data['password']

    # 2. Look up the user in the database
    session = Session()
    try:
        user = session.query(User).filter_by(username=username).first()

        # 3. Verify credentials
        # IMPORTANT: We use a generic error message to avoid leaking information
        # about whether a username exists or not (security best practice).
        if not user or not user.check_password(password):
            return jsonify({
                "error": "Unauthorized",
                "message": "Invalid username or password."
            }), 401

        # 4. Generate JWT Token
        # The token payload contains "claims" — pieces of data we embed:
        #   - 'user_id': So we know which user owns this token
        #   - 'username': For convenience (avoids extra DB queries)
        #   - 'exp': Expiration time — after this, the token is invalid
        #   - 'iat': Issued At — when the token was created
        token_payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=TOKEN_EXPIRATION_MINUTES),
            'iat': datetime.datetime.utcnow()
        }

        # jwt.encode() creates the token string.
        # We sign it with our SECRET_KEY using the HS256 algorithm.
        # Anyone with the SECRET_KEY can verify (and forge!) tokens,
        # so the key MUST be kept secret.
        token = jwt.encode(
            token_payload,
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )

        return jsonify({
            "message": "Login successful",
            "token": token,
            "expires_in": f"{TOKEN_EXPIRATION_MINUTES} minutes"
        }), 200

    finally:
        session.close()


# --- Token Decode Demo Route (for learning/debugging) ---

@app.route('/decode-token', methods=['POST'])
def decode_token():
    """
    POST /decode-token
    
    A helper endpoint to decode and inspect a JWT token.
    This is for LEARNING purposes only — in production, you would
    never expose an endpoint that decodes arbitrary tokens!
    
    Request Body (JSON):
        { "token": "eyJhbGciOiJIUzI1NiIs..." }
    
    Response:
        { "payload": { "user_id": 1, "username": "john", ... } }
    """
    data = request.get_json(silent=True)
    if not data or 'token' not in data:
        raise BadRequest("Field 'token' is required.")

    try:
        # jwt.decode() verifies the signature and checks expiration
        payload = jwt.decode(
            data['token'],
            app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return jsonify({
            "message": "Token is valid",
            "payload": payload
        }), 200

    except jwt.ExpiredSignatureError:
        return jsonify({
            "error": "Token Expired",
            "message": "The token has expired. Please login again."
        }), 401

    except jwt.InvalidTokenError:
        return jsonify({
            "error": "Invalid Token",
            "message": "The token is invalid or has been tampered with."
        }), 401


if __name__ == '__main__':
    print("\n=== Exercise 8.2: Login Endpoint with JWT ===")
    print("Steps to test:")
    print("  1. Register:  POST /register  {username, email, password}")
    print("  2. Login:     POST /login     {username, password}")
    print("  3. Decode:    POST /decode-token {token}")
    print(f"  Token expires after {TOKEN_EXPIRATION_MINUTES} minutes.\n")
    app.run(debug=True, port=5000)
