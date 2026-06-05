# =====================================================================
# EXERCISE 8.4: PROTECTED ROUTES
# =====================================================================
# Goal: Build a complete set of protected API routes that demonstrate:
#   - Public vs. Protected route separation
#   - Role-based access control (admin vs. regular user)
#   - User-specific data access (each user sees only their own data)
#   - Different protection levels for different endpoints
#
# Key Concepts:
#   - Authorization vs. Authentication:
#       Authentication = "Who are you?" (handled by login + JWT)
#       Authorization  = "What can you do?" (handled by roles/permissions)
#
#   - Role-Based Access Control (RBAC):
#       Different users have different roles (e.g., 'user', 'admin')
#       Each role grants access to different endpoints/actions
#
# Dependencies: pip install flask sqlalchemy PyJWT werkzeug
# =====================================================================

import jwt
import datetime
from functools import wraps
from flask import Flask, jsonify, request, g
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-super-secret-key-change-in-production'
TOKEN_EXPIRATION_MINUTES = 30

# --- Database Setup ---
engine = create_engine('sqlite:///exercise_8_4.db', echo=False)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(256), nullable=False)
    is_admin = Column(Boolean, default=False)  # NEW: Role flag

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin
        }


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# =====================================================================
# DECORATORS: Two levels of protection
# =====================================================================

def token_required(f):
    """
    Basic protection: Requires a valid JWT token.
    Any authenticated user can access routes with this decorator.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]

        if not token:
            return jsonify({
                "error": "Unauthorized",
                "message": "Token is missing. Provide it as: Authorization: Bearer <token>"
            }), 401

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token Expired", "message": "Please login again."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid Token", "message": "Token is invalid."}), 401

        session = Session()
        try:
            current_user = session.query(User).filter_by(id=payload['user_id']).first()
            if not current_user:
                return jsonify({"error": "Unauthorized", "message": "User not found."}), 401
            g.db_session = session
            return f(current_user, *args, **kwargs)
        finally:
            session.close()

    return decorated


def admin_required(f):
    """
    Admin protection: Requires a valid JWT token AND admin privileges.
    
    This decorator STACKS with @token_required conceptually, but we
    implement it as a standalone decorator that does both checks.
    
    Usage:
        @app.route('/admin-only')
        @admin_required
        def admin_dashboard(current_user):
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]

        if not token:
            return jsonify({
                "error": "Unauthorized",
                "message": "Token is missing."
            }), 401

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token Expired", "message": "Please login again."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid Token", "message": "Token is invalid."}), 401

        session = Session()
        try:
            current_user = session.query(User).filter_by(id=payload['user_id']).first()
            if not current_user:
                return jsonify({"error": "Unauthorized", "message": "User not found."}), 401

            # EXTRA CHECK: Is this user an admin?
            if not current_user.is_admin:
                return jsonify({
                    "error": "Forbidden",
                    "message": "Admin access required. You do not have permission."
                }), 403  # 403 Forbidden, NOT 401 Unauthorized

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


# =====================================================================
# PUBLIC ROUTES (no token needed)
# =====================================================================

@app.route('/', methods=['GET'])
def home():
    """GET / - API overview with all available endpoints."""
    return jsonify({
        "message": "Exercise 8.4 - Protected Routes with Role-Based Access",
        "public_endpoints": {
            "GET /": "This page",
            "POST /register": "Create a new account",
            "POST /login": "Login and receive JWT token"
        },
        "protected_endpoints (token required)": {
            "GET /profile": "View your own profile",
            "PUT /profile": "Update your own profile",
            "DELETE /profile": "Delete your own account"
        },
        "admin_endpoints (admin token required)": {
            "GET /admin/users": "List all users",
            "DELETE /admin/users/<id>": "Delete any user",
            "PUT /admin/users/<id>/promote": "Promote user to admin"
        }
    }), 200


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
        raise BadRequest("Username must be a non-empty string.")
    if not email or '@' not in email:
        raise BadRequest("Email must be a valid email address.")
    if len(password) < 6:
        raise BadRequest("Password must be at least 6 characters.")

    session = Session()
    try:
        if session.query(User).filter_by(username=username).first():
            return jsonify({"error": "Conflict", "message": "Username already exists."}), 409
        if session.query(User).filter_by(email=email).first():
            return jsonify({"error": "Conflict", "message": "Email already registered."}), 409

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        # First user gets admin privileges automatically!
        if session.query(User).count() == 0:
            new_user.is_admin = True

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
            'is_admin': user.is_admin,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=TOKEN_EXPIRATION_MINUTES),
            'iat': datetime.datetime.utcnow()
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
            "message": "Login successful",
            "token": token,
            "is_admin": user.is_admin
        }), 200
    finally:
        session.close()


# =====================================================================
# PROTECTED ROUTES (any authenticated user)
# =====================================================================

@app.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """GET /profile - View your own profile. Requires token."""
    return jsonify({"user": current_user.to_dict()}), 200


@app.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """
    PUT /profile - Update your own profile (email only).
    
    This demonstrates that a user can ONLY modify their OWN data.
    The decorator ensures we know exactly who is making the request.
    """
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Invalid JSON format or missing Request Body.")

    session = Session()
    try:
        user = session.query(User).filter_by(id=current_user.id).first()

        if 'email' in data:
            email = data['email'].strip().lower()
            if not email or '@' not in email:
                raise BadRequest("Invalid email format.")
            existing = session.query(User).filter_by(email=email).first()
            if existing and existing.id != user.id:
                return jsonify({"error": "Conflict", "message": "Email already in use."}), 409
            user.email = email

        if 'password' in data:
            password = data['password']
            if len(password) < 6:
                raise BadRequest("Password must be at least 6 characters.")
            user.set_password(password)

        session.commit()
        return jsonify({"message": "Profile updated", "user": user.to_dict()}), 200
    except BadRequest:
        raise
    except Exception as e:
        session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        session.close()


@app.route('/profile', methods=['DELETE'])
@token_required
def delete_profile(current_user):
    """DELETE /profile - Delete your own account. Requires token."""
    session = Session()
    try:
        user = session.query(User).filter_by(id=current_user.id).first()
        if user:
            session.delete(user)
            session.commit()
        return jsonify({"message": f"Account '{current_user.username}' deleted successfully."}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        session.close()


# =====================================================================
# ADMIN-ONLY ROUTES (requires admin role)
# =====================================================================

@app.route('/admin/users', methods=['GET'])
@admin_required
def admin_list_users(current_user):
    """
    GET /admin/users - List ALL users in the system.
    Only admins can see all users — regular users can only see themselves.
    """
    session = Session()
    try:
        users = session.query(User).all()
        return jsonify({
            "total_users": len(users),
            "users": [u.to_dict() for u in users]
        }), 200
    finally:
        session.close()


@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(current_user, user_id):
    """DELETE /admin/users/<id> - Admin can delete any user."""
    if current_user.id == user_id:
        return jsonify({"error": "Bad Request", "message": "Admins cannot delete themselves."}), 400

    session = Session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "Not Found", "message": f"User ID {user_id} not found."}), 404
        
        username = user.username
        session.delete(user)
        session.commit()
        return jsonify({"message": f"User '{username}' deleted by admin."}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        session.close()


@app.route('/admin/users/<int:user_id>/promote', methods=['PUT'])
@admin_required
def admin_promote_user(current_user, user_id):
    """PUT /admin/users/<id>/promote - Promote a user to admin."""
    session = Session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "Not Found", "message": f"User ID {user_id} not found."}), 404
        
        if user.is_admin:
            return jsonify({"message": f"User '{user.username}' is already an admin."}), 200

        user.is_admin = True
        session.commit()
        return jsonify({"message": f"User '{user.username}' promoted to admin.", "user": user.to_dict()}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        session.close()


if __name__ == '__main__':
    print("\n=== Exercise 8.4: Protected Routes ===")
    print("Route Access Levels:")
    print("  PUBLIC:     GET /  |  POST /register  |  POST /login")
    print("  PROTECTED:  GET/PUT/DELETE /profile")
    print("  ADMIN ONLY: GET /admin/users  |  DELETE /admin/users/<id>  |  PUT /admin/users/<id>/promote")
    print("\nTip: First registered user automatically becomes admin!\n")
    app.run(debug=True, port=5000)
