# =====================================================================
# MINI PROJECT: TODO APP WITH AUTHENTICATION
# =====================================================================
# A complete REST API that combines everything from Exercises 8.1–8.4:
#
# Features:
#   ✅ User Registration & Login with JWT tokens
#   ✅ Each user can only see their OWN todos
#   ✅ Only the owner can create, edit, and delete their todos
#   ✅ Token-based authentication on all todo endpoints
#   ✅ Proper error handling and input validation
#   ✅ SQLAlchemy ORM with relationships (User ↔ Todo)
#
# API Endpoints:
#   PUBLIC:
#     POST   /auth/register       - Create a new account
#     POST   /auth/login           - Login and get JWT token
#
#   PROTECTED (requires Bearer token):
#     GET    /auth/me               - View current user profile
#     GET    /todos                 - List YOUR todos (with filters)
#     POST   /todos                 - Create a new todo
#     GET    /todos/<id>            - View a specific todo (yours only)
#     PUT    /todos/<id>            - Update a todo (yours only)
#     DELETE /todos/<id>            - Delete a todo (yours only)
#     GET    /todos/stats           - Get your todo statistics
#
# Dependencies: pip install flask sqlalchemy PyJWT werkzeug
# =====================================================================

import jwt
import datetime
from functools import wraps
from flask import Flask, jsonify, request, g
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest, NotFound

app = Flask(__name__)
app.config['SECRET_KEY'] = 'todo-app-secret-key-change-in-production'
TOKEN_EXPIRATION_MINUTES = 60


# =====================================================================
# 1. DATABASE SETUP
# =====================================================================

engine = create_engine('sqlite:///todo_app_auth.db', echo=False)
Base = declarative_base()


# =====================================================================
# 2. MODELS
# =====================================================================

class User(Base):
    """
    User model. Each user can have many todos (One-to-Many relationship).
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # One-to-Many: A user can have many todos.
    # cascade='all, delete-orphan' means if a user is deleted,
    # all their todos are automatically deleted too.
    todos = relationship('Todo', back_populates='owner', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "todo_count": len(self.todos)
        }

    def __repr__(self):
        return f"<User('{self.username}')>"


class Todo(Base):
    """
    Todo model. Each todo belongs to exactly one user (Many-to-One).
    """
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), default="")
    completed = Column(Boolean, default=False)
    priority = Column(String(10), default="medium")  # low, medium, high
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Foreign Key: Links this todo to a specific user
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Reverse relationship: Access the User from a Todo
    owner = relationship('User', back_populates='todos')

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "owner": self.owner.username if self.owner else None
        }

    def __repr__(self):
        status = "DONE" if self.completed else "PENDING"
        return f"<Todo('{self.title}', {status})>"


# Create all tables
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# =====================================================================
# 3. TOKEN VALIDATION DECORATOR
# =====================================================================

def token_required(f):
    """
    Decorator that protects routes by requiring a valid JWT token.
    Injects 'current_user' as the first argument to the wrapped function.
    Also stores a DB session in g.db_session for use in the route.
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
                "message": "Token is missing. Include header: Authorization: Bearer <token>"
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

            # Store the session so routes can use it for DB operations
            g.db_session = session
            result = f(current_user, *args, **kwargs)
            return result
        finally:
            session.close()

    return decorated


# =====================================================================
# 4. ERROR HANDLERS
# =====================================================================

@app.errorhandler(400)
def bad_request(error):
    message = error.description if hasattr(error, 'description') else "Bad request"
    return jsonify({"error": "Bad Request", "message": message}), 400

@app.errorhandler(404)
def not_found(error):
    message = error.description if hasattr(error, 'description') else "Resource not found"
    return jsonify({"error": "Not Found", "message": message}), 404

@app.errorhandler(401)
def unauthorized(error):
    message = error.description if hasattr(error, 'description') else "Unauthorized"
    return jsonify({"error": "Unauthorized", "message": message}), 401

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."}), 500


# =====================================================================
# 5. PUBLIC ROUTES: Authentication
# =====================================================================

@app.route('/', methods=['GET'])
def home():
    """GET / - API overview."""
    return jsonify({
        "app": "Todo App with Authentication",
        "version": "1.0",
        "endpoints": {
            "auth": {
                "POST /auth/register": "Create a new account",
                "POST /auth/login": "Login and get JWT token",
                "GET /auth/me": "View current user profile (token required)"
            },
            "todos": {
                "GET /todos": "List your todos (token required)",
                "POST /todos": "Create a new todo (token required)",
                "GET /todos/<id>": "View a specific todo (token required)",
                "PUT /todos/<id>": "Update a todo (token required)",
                "DELETE /todos/<id>": "Delete a todo (token required)",
                "GET /todos/stats": "Get your todo statistics (token required)"
            }
        }
    }), 200


@app.route('/auth/register', methods=['POST'])
def register():
    """
    POST /auth/register
    
    Creates a new user account.
    
    Request Body:
        { "username": "john", "email": "john@example.com", "password": "secret123" }
    """
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Invalid JSON format or missing Request Body.")

    # Validate required fields
    for field in ['username', 'email', 'password']:
        if field not in data:
            raise BadRequest(f"Field '{field}' is required.")

    username = str(data['username']).strip()
    email = str(data['email']).strip().lower()
    password = str(data['password'])

    if not username:
        raise BadRequest("Username must be a non-empty string.")
    if len(username) < 3:
        raise BadRequest("Username must be at least 3 characters.")
    if not email or '@' not in email or '.' not in email:
        raise BadRequest("A valid email address is required.")
    if len(password) < 6:
        raise BadRequest("Password must be at least 6 characters.")

    session = Session()
    try:
        # Check uniqueness
        if session.query(User).filter_by(username=username).first():
            return jsonify({"error": "Conflict", "message": "Username already exists."}), 409
        if session.query(User).filter_by(email=email).first():
            return jsonify({"error": "Conflict", "message": "Email already registered."}), 409

        # Create user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        session.add(new_user)
        session.commit()

        return jsonify({
            "message": "User registered successfully!",
            "user": new_user.to_dict()
        }), 201

    except Exception as e:
        session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        session.close()


@app.route('/auth/login', methods=['POST'])
def login():
    """
    POST /auth/login
    
    Authenticates a user and returns a JWT token.
    
    Request Body:
        { "username": "john", "password": "secret123" }
    
    Response:
        { "message": "Login successful", "token": "eyJ...", "user": {...} }
    """
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Invalid JSON format or missing Request Body.")
    if 'username' not in data or 'password' not in data:
        raise BadRequest("Fields 'username' and 'password' are required.")

    session = Session()
    try:
        user = session.query(User).filter_by(username=data['username']).first()

        if not user or not user.check_password(data['password']):
            return jsonify({
                "error": "Unauthorized",
                "message": "Invalid username or password."
            }), 401

        # Generate JWT token
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=TOKEN_EXPIRATION_MINUTES),
            'iat': datetime.datetime.utcnow()
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
            "message": "Login successful!",
            "token": token,
            "expires_in": f"{TOKEN_EXPIRATION_MINUTES} minutes",
            "user": user.to_dict()
        }), 200

    finally:
        session.close()


@app.route('/auth/me', methods=['GET'])
@token_required
def get_me(current_user):
    """GET /auth/me - View the current authenticated user's profile."""
    return jsonify({"user": current_user.to_dict()}), 200


# =====================================================================
# 6. PROTECTED ROUTES: Todo CRUD
# =====================================================================

@app.route('/todos', methods=['GET'])
@token_required
def get_todos(current_user):
    """
    GET /todos - List all todos for the CURRENT USER only.
    
    Query Parameters (optional filters):
        ?completed=true     - Show only completed todos
        ?completed=false    - Show only pending todos
        ?priority=high      - Filter by priority (low/medium/high)
        ?search=keyword     - Search in title and description
    
    KEY SECURITY CONCEPT:
        We filter by user_id=current_user.id, so a user can NEVER
        see another user's todos, even if they guess the todo ID.
    """
    session = Session()
    try:
        # Start with todos belonging to the current user ONLY
        query = session.query(Todo).filter_by(user_id=current_user.id)

        # Apply optional filters
        completed_filter = request.args.get('completed')
        if completed_filter is not None:
            if completed_filter.lower() == 'true':
                query = query.filter_by(completed=True)
            elif completed_filter.lower() == 'false':
                query = query.filter_by(completed=False)

        priority_filter = request.args.get('priority')
        if priority_filter and priority_filter.lower() in ['low', 'medium', 'high']:
            query = query.filter_by(priority=priority_filter.lower())

        search_filter = request.args.get('search')
        if search_filter:
            search_term = f"%{search_filter}%"
            query = query.filter(
                (Todo.title.ilike(search_term)) | (Todo.description.ilike(search_term))
            )

        # Order: incomplete first, then by priority, then by creation date
        todos = query.order_by(Todo.completed, Todo.created_at.desc()).all()

        return jsonify({
            "count": len(todos),
            "todos": [t.to_dict() for t in todos]
        }), 200

    finally:
        session.close()


@app.route('/todos', methods=['POST'])
@token_required
def create_todo(current_user):
    """
    POST /todos - Create a new todo for the current user.
    
    Request Body:
        {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",   (optional)
            "priority": "high"                      (optional: low/medium/high)
        }
    """
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Invalid JSON format or missing Request Body.")

    if 'title' not in data:
        raise BadRequest("Field 'title' is required.")

    title = str(data['title']).strip()
    if not title:
        raise BadRequest("Field 'title' must be a non-empty string.")
    if len(title) > 100:
        raise BadRequest("Field 'title' cannot exceed 100 characters.")

    description = str(data.get('description', '')).strip()
    priority = str(data.get('priority', 'medium')).strip().lower()

    if priority not in ['low', 'medium', 'high']:
        raise BadRequest("Field 'priority' must be 'low', 'medium', or 'high'.")

    session = Session()
    try:
        new_todo = Todo(
            title=title,
            description=description,
            priority=priority,
            user_id=current_user.id  # Assign to the current user!
        )
        session.add(new_todo)
        session.commit()

        return jsonify({
            "message": "Todo created successfully!",
            "todo": new_todo.to_dict()
        }), 201

    except Exception as e:
        session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        session.close()


@app.route('/todos/stats', methods=['GET'])
@token_required
def get_todo_stats(current_user):
    """
    GET /todos/stats - Get statistics about the current user's todos.
    
    NOTE: This route is defined BEFORE /todos/<int:todo_id> to avoid
    Flask interpreting 'stats' as a todo_id parameter.
    """
    session = Session()
    try:
        todos = session.query(Todo).filter_by(user_id=current_user.id).all()

        total = len(todos)
        completed = sum(1 for t in todos if t.completed)
        pending = total - completed

        # Count by priority
        priority_counts = {"low": 0, "medium": 0, "high": 0}
        for t in todos:
            if t.priority in priority_counts:
                priority_counts[t.priority] += 1

        return jsonify({
            "username": current_user.username,
            "statistics": {
                "total": total,
                "completed": completed,
                "pending": pending,
                "completion_rate": f"{(completed / total * 100):.1f}%" if total > 0 else "N/A",
                "by_priority": priority_counts
            }
        }), 200

    finally:
        session.close()


@app.route('/todos/<int:todo_id>', methods=['GET'])
@token_required
def get_todo(current_user, todo_id):
    """
    GET /todos/<id> - View a specific todo.
    
    OWNERSHIP CHECK: Only the owner can view their todo.
    If a user tries to access another user's todo, they get 404
    (we return 404 instead of 403 to avoid revealing that the todo exists).
    """
    session = Session()
    try:
        # Filter by BOTH todo_id AND user_id — this is the ownership check!
        todo = session.query(Todo).filter_by(id=todo_id, user_id=current_user.id).first()

        if not todo:
            return jsonify({
                "error": "Not Found",
                "message": f"Todo with ID {todo_id} not found."
            }), 404

        return jsonify({"todo": todo.to_dict()}), 200

    finally:
        session.close()


@app.route('/todos/<int:todo_id>', methods=['PUT'])
@token_required
def update_todo(current_user, todo_id):
    """
    PUT /todos/<id> - Update a todo (owner only).
    
    Request Body (all fields optional):
        {
            "title": "Updated title",
            "description": "Updated description",
            "completed": true,
            "priority": "high"
        }
    """
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Invalid JSON format or missing Request Body.")

    session = Session()
    try:
        # OWNERSHIP CHECK: only the owner can update
        todo = session.query(Todo).filter_by(id=todo_id, user_id=current_user.id).first()

        if not todo:
            return jsonify({
                "error": "Not Found",
                "message": f"Todo with ID {todo_id} not found."
            }), 404

        # Validate and update each field if provided
        if 'title' in data:
            title = str(data['title']).strip()
            if not title:
                raise BadRequest("Field 'title' must be a non-empty string.")
            if len(title) > 100:
                raise BadRequest("Field 'title' cannot exceed 100 characters.")
            todo.title = title

        if 'description' in data:
            todo.description = str(data['description']).strip()

        if 'completed' in data:
            if not isinstance(data['completed'], bool):
                raise BadRequest("Field 'completed' must be a boolean (true/false).")
            todo.completed = data['completed']

        if 'priority' in data:
            priority = str(data['priority']).strip().lower()
            if priority not in ['low', 'medium', 'high']:
                raise BadRequest("Field 'priority' must be 'low', 'medium', or 'high'.")
            todo.priority = priority

        todo.updated_at = datetime.datetime.utcnow()
        session.commit()

        return jsonify({
            "message": "Todo updated successfully!",
            "todo": todo.to_dict()
        }), 200

    except BadRequest:
        raise
    except Exception as e:
        session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        session.close()


@app.route('/todos/<int:todo_id>', methods=['DELETE'])
@token_required
def delete_todo(current_user, todo_id):
    """
    DELETE /todos/<id> - Delete a todo (owner only).
    
    Only the owner of the todo can delete it. If someone else tries,
    they'll get a 404 (the todo doesn't exist *for them*).
    """
    session = Session()
    try:
        # OWNERSHIP CHECK: only the owner can delete
        todo = session.query(Todo).filter_by(id=todo_id, user_id=current_user.id).first()

        if not todo:
            return jsonify({
                "error": "Not Found",
                "message": f"Todo with ID {todo_id} not found."
            }), 404

        title = todo.title
        session.delete(todo)
        session.commit()

        return jsonify({
            "message": f"Todo '{title}' deleted successfully!",
            "deleted_id": todo_id
        }), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        session.close()


# =====================================================================
# 7. MAIN ENTRY POINT
# =====================================================================

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║           TODO APP WITH AUTHENTICATION                      ║
║                   Mini Project - Week 8                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  AUTH ENDPOINTS:                                             ║
║    POST   /auth/register    Register a new account           ║
║    POST   /auth/login       Login & get JWT token            ║
║    GET    /auth/me          View your profile                ║
║                                                              ║
║  TODO ENDPOINTS (all require token):                         ║
║    GET    /todos            List your todos                  ║
║    POST   /todos            Create a todo                    ║
║    GET    /todos/<id>       View a todo                      ║
║    PUT    /todos/<id>       Update a todo                    ║
║    DELETE /todos/<id>       Delete a todo                    ║
║    GET    /todos/stats      Your todo statistics             ║
║                                                              ║
║  KEY RULES:                                                  ║
║    • Each user can ONLY see their own todos                  ║
║    • Only the OWNER can edit/delete a todo                   ║
║    • Tokens expire after 60 minutes                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
    app.run(debug=True, port=5000)
