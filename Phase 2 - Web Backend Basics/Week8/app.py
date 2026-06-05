import datetime
from functools import wraps

import jwt
from flask import Flask, jsonify, request
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'

# Database Setup
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], connect_args={'check_same_thread': False})
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    todos = relationship('Todo', back_populates='owner')

class Todo(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(250))
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner = relationship('User', back_populates='todos')

Base.metadata.create_all(engine)

# Exercise 8.3: Token validation decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                token = auth_header
                
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
            
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = session.query(User).filter_by(id=data['user_id']).first()
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

# Exercise 8.1: Create register endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Must provide username and password'}), 400
        
    username = data.get('username')
    password = data.get('password')
    
    existing_user = session.query(User).filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'User already exists!'}), 409
        
    hashed_password = generate_password_hash(password)
    
    new_user = User(username=username, password_hash=hashed_password)
    session.add(new_user)
    session.commit()
    
    return jsonify({'message': 'User created successfully!'}), 201

# Exercise 8.2: Create login endpoint (return JWT token)
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic realm="Login required!"'}), 401
        
    user = session.query(User).filter_by(username=data.get('username')).first()
    
    if not user:
        return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic realm="Login required!"'}), 401
        
    if check_password_hash(user.password_hash, data.get('password')):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({'token': token})
        
    return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic realm="Login required!"'}), 401

# Exercise 8.4 & Mini Project: Protected routes (Todo App)

@app.route('/todos', methods=['GET'])
@token_required
def get_all_todos(current_user):
    # Mỗi user chỉ xem được todos của mình
    todos = session.query(Todo).filter_by(user_id=current_user.id).all()
    
    output = []
    for todo in todos:
        todo_data = {
            'id': todo.id,
            'title': todo.title,
            'description': todo.description,
            'completed': todo.completed
        }
        output.append(todo_data)
        
    return jsonify({'todos': output})

@app.route('/todos/<int:todo_id>', methods=['GET'])
@token_required
def get_one_todo(current_user, todo_id):
    # Only owner
    todo = session.query(Todo).filter_by(id=todo_id, user_id=current_user.id).first()
    
    if not todo:
        return jsonify({'message': 'No todo found!'}), 404
        
    todo_data = {
        'id': todo.id,
        'title': todo.title,
        'description': todo.description,
        'completed': todo.completed
    }
    
    return jsonify(todo_data)

@app.route('/todos', methods=['POST'])
@token_required
def create_todo(current_user):
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'message': 'Title is required'}), 400
        
    new_todo = Todo(
        title=data.get('title'),
        description=data.get('description', ''),
        completed=False,
        user_id=current_user.id
    )
    
    session.add(new_todo)
    session.commit()
    
    return jsonify({'message': 'Todo created!'}), 201

@app.route('/todos/<int:todo_id>', methods=['PUT'])
@token_required
def update_todo(current_user, todo_id):
    # Only owner có thể edit/delete
    todo = session.query(Todo).filter_by(id=todo_id, user_id=current_user.id).first()
    
    if not todo:
        return jsonify({'message': 'No todo found or you are not the owner!'}), 404
        
    data = request.get_json()
    
    if 'title' in data:
        todo.title = data['title']
    if 'description' in data:
        todo.description = data['description']
    if 'completed' in data:
        todo.completed = data['completed']
        
    session.commit()
    
    return jsonify({'message': 'Todo updated!'})

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
@token_required
def delete_todo(current_user, todo_id):
    # Only owner có thể edit/delete
    todo = session.query(Todo).filter_by(id=todo_id, user_id=current_user.id).first()
    
    if not todo:
        return jsonify({'message': 'No todo found or you are not the owner!'}), 404
        
    session.delete(todo)
    session.commit()
    
    return jsonify({'message': 'Todo deleted!'})

if __name__ == '__main__':
    app.run(debug=True)
