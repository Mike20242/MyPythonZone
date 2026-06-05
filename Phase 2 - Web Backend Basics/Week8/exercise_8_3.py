# =====================================================================
# EXERCISE 8.3: TOKEN VALIDATION DECORATOR
# =====================================================================
# Goal: Create a reusable decorator that:
#   - Extracts the JWT token from the Authorization header
#   - Validates and decodes the token
#   - Passes the current user's info to the protected route
#   - Returns appropriate errors for missing/invalid/expired tokens
#
# Key Concepts:
#   - Python Decorators: Functions that wrap other functions to add
#     behavior (like authentication checks) without modifying the
#     original function's code.
#
#   - Authorization Header Format:
#       Authorization: Bearer <token>
#     The "Bearer" scheme is the standard way to send JWT tokens
#     in HTTP requests.
#
#   - functools.wraps: Preserves the original function's metadata
#     (name, docstring) when wrapping it — important for Flask to
#     correctly identify routes.
#
# Dependencies: pip install flask sqlalchemy PyJWT werkzeug
# =====================================================================

import jwt
import datetime
from functools import wraps
from flask import Flask, jsonify, request, g
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-super-secret-key-change-in-production'
TOKEN_EXPIRATION_MINUTES = 30

# --- Database Setup ---
engine = create_engine('sqlite:///exercise_8_3.db', echo=False)
Base = declarative_base()


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
        return {"id": self.id, "username": self.username, "email": self.email}


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# =====================================================================
# THE TOKEN VALIDATION DECORATOR (CORE OF THIS EXERCISE)
# =====================================================================

def token_required(f):
    """
    A decorator that protects routes by requiring a valid JWT token.
    
    How it works:
    1. Checks for the 'Authorization' header in the request
    2. Extracts the token from "Bearer <token>" format
    3. Decodes and validates the token using our SECRET_KEY
    4. Looks up the user in the database to ensure they still exist
    5. Passes the 'current_user' as the first argument to the wrapped function
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_route(current_user):
            return jsonify({"message": f"Hello, {current_user.username}!"})
    
    Error Responses:
        401 - Token missing, expired, invalid, or user not found
    """
    @wraps(f)  # Preserves original function's __name__ and __doc__
    def decorated(*args, **kwargs):
        token = None

        # --- Step 1: Extract the token from the Authorization header ---
        # Expected format: "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            parts = auth_header.split()
            # Validate the format: must be "Bearer <token>" (exactly 2 parts)
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]

        if not token:
            return jsonify({
                "error": "Unauthorized",
                "message": "Token is missing. Provide it as: Authorization: Bearer <token>"
            }), 401

        # --- Step 2: Decode and validate the token ---
        try:
            payload = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            # The payload contains the claims we put in during login:
            # {'user_id': 1, 'username': 'john', 'exp': ..., 'iat': ...}
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "Token Expired",
                "message": "Your token has expired. Please login again."
            }), 401

        except jwt.InvalidTokenError:
            return jsonify({
                "error": "Invalid Token",
                "message": "The token is invalid or has been tampered with."
            }), 401

        # --- Step 3: Look up the user in the database ---
        # Even if the token is valid, the user might have been deleted.
        session = Session()
        try:
            current_user = session.query(User).filter_by(id=payload['user_id']).first()
            
            if not current_user:
                return jsonify({
                    "error": "Unauthorized",
                    "message": "User associated with this token no longer exists."
                }), 401

            # --- Step 4: Call the original function with current_user ---
            # We store the session in Flask's g object so the route can use it,
            # and pass current_user as the first argument.
            g.db_session = session
            return f(current_user, *args, **kwargs)

        finally:
            session.close()

    return decorated


# --- Error Handlers ---

@app.errorhandler(400)
def bad_request(error):
    message = error.description if hasattr(error, 'description') else "Bad request"
    return jsonify({"error": "Bad Request", "message": message}), 400


# --- Auth Routes (Register & Login from previous exercises) ---

@app.route('/register', methods=['POST'])
def register():
    """POST /register - Create a new user account."""
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Invalid JSON format or missing Request Body.")

    for field in ['username', 'email', 'password']:
        if field not in data:
            raise BadRequest(f"Field '{field}' is required.")

    username = data['username'].strip()
    email = data['email'].strip().lower()
    password = data['password']

    if not username:
        raise BadRequest("Field 'username' must be a non-empty string.")
    if not email or '@' not in email:
        raise BadRequest("Field 'email' must be a valid email address.")
    if len(password) < 6:
        raise BadRequest("Field 'password' must be at least 6 characters.")

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
        return jsonify({"message": "User registered successfully", "user": new_user.to_dict()}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        session.close()


@app.route('/login', methods=['POST'])
def login():
    """POST /login - Authenticate and return JWT token."""
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Invalid JSON format or missing Request Body.")
    if 'username' not in data or 'password' not in data:
        raise BadRequest("Fields 'username' and 'password' are required.")

    session = Session()
    try:
        user = session.query(User).filter_by(username=data['username']).first()
        if not user or not user.check_password(data['password']):
            return jsonify({"error": "Unauthorized", "message": "Invalid username or password."}), 401

        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=TOKEN_EXPIRATION_MINUTES),
            'iat': datetime.datetime.utcnow()
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({"message": "Login successful", "token": token}), 200
    finally:
        session.close()


# =====================================================================
# DEMONSTRATION: Using the @token_required decorator
# =====================================================================

@app.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """
    GET /profile
    
    A protected route that returns the current user's profile.
    Notice how 'current_user' is automatically injected by @token_required!
    
    Headers Required:
        Authorization: Bearer <your-jwt-token>
    """
    return jsonify({
        "message": f"Welcome to your profile, {current_user.username}!",
        "user": current_user.to_dict()
    }), 200


@app.route('/secret', methods=['GET'])
@token_required
def secret_data(current_user):
    """
    GET /secret
    
    Another protected route — only accessible with a valid token.
    This demonstrates that the decorator can be reused on any route.
    """
    return jsonify({
        "message": "You have accessed the secret area!",
        "secret": "The answer to life, the universe, and everything is 42.",
        "accessed_by": current_user.username
    }), 200


# --- Public route (no token needed) ---

@app.route('/', methods=['GET'])
def home():
    """GET / - Public home page, no authentication required."""
    return jsonify({
        "message": "Welcome to Exercise 8.3 - Token Validation Decorator!",
        "endpoints": {
            "POST /register": "Create a new account",
            "POST /login": "Login and get a JWT token",
            "GET /profile": "View your profile (token required)",
            "GET /secret": "Access secret data (token required)"
        }
    }), 200


if __name__ == '__main__':
    print("\n=== Exercise 8.3: Token Validation Decorator ===")
    print("Test flow:")
    print("  1. POST /register  → Create an account")
    print("  2. POST /login     → Get your token")
    print("  3. GET  /profile   → Use token: Authorization: Bearer <token>")
    print("  4. GET  /secret    → Another protected route")
    print("  5. GET  /          → Public (no token needed)\n")
    app.run(debug=True, port=5000)
