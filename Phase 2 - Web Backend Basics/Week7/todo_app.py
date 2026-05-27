from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os
import hashlib

# =====================================================================
# MINI PROJECT: TODO APP BACKEND WITH DATABASE (INTERACTIVE CLI)
# =====================================================================

# 1. Database Setup
db_path = 'todo_app.db'
engine = create_engine(f'sqlite:///{db_path}', echo=False)

# Base class for all declarative models
Base = declarative_base()

# =====================================================================
# 2. MODELS DEFINITION
# =====================================================================

class User(Base):
    """
    User model representing a person who can own multiple Todo items.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False) # Hashed password for security

    # One-to-Many relationship with Todo (Cascade delete enabled)
    todos = relationship('Todo', back_populates='owner', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User('{self.username}')>"


class Todo(Base):
    """
    Todo model representing a task that belongs to a specific User.
    """
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), default="")
    completed = Column(Boolean, default=False)
    
    # Foreign Key linking back to the User table
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Reverse relationship to access the User from a Todo
    owner = relationship('User', back_populates='todos')

    def __repr__(self):
        status = "DONE" if self.completed else "PENDING"
        return f"<Todo('{self.title}', status='{status}')>"


# Create all tables in the database engine
Base.metadata.create_all(engine)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)


# =====================================================================
# 3. SECURITY UTILS
# =====================================================================

def hash_password(password):
    """Hashes a password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()


# =====================================================================
# 4. APPLICATION LOGIC / CRUD FUNCTIONS
# =====================================================================

def register_user(username, email, password):
    """Creates a new user and saves it to the database with a hashed password."""
    session = Session()
    try:
        # Check if username or email already exists
        if session.query(User).filter_by(username=username).first():
            print("[!] Username already exists.")
            return None
        if session.query(User).filter_by(email=email).first():
            print("[!] Email already registered.")
            return None
            
        hashed_pw = hash_password(password)
        new_user = User(username=username, email=email, password=hashed_pw)
        session.add(new_user)
        session.commit()
        print(f"[*] User '{username}' registered successfully!")
        return new_user.id
    except Exception as e:
        session.rollback()
        print(f"[!] Registration error: {e}")
    finally:
        session.close()

def authenticate_user(username, password):
    """Validates user credentials and returns the user ID if successful."""
    session = Session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user and user.password == hash_password(password):
            print(f"[*] Login successful. Welcome back, {username}!")
            return user.id
        print("[!] Invalid username or password.")
        return None
    finally:
        session.close()

def create_todo(user_id, title, description=""):
    """Creates a new todo item for a specific user."""
    session = Session()
    try:
        new_todo = Todo(title=title, description=description, user_id=user_id)
        session.add(new_todo)
        session.commit()
        print(f"[*] Todo '{title}' created successfully.")
    except Exception as e:
        session.rollback()
        print(f"[!] Error creating todo: {e}")
    finally:
        session.close()

def list_todos(user_id):
    """Retrieves all todos for a specific user, ordering by completion status."""
    session = Session()
    try:
        # Order so that pending tasks show up before completed tasks.
        todos = session.query(Todo).filter_by(user_id=user_id).order_by(Todo.completed).all()
        if not todos:
            print("\n--- You have no todos yet! ---")
            return
            
        print("\n--- Your Todos ---")
        for t in todos:
            status = "[x]" if t.completed else "[ ]"
            desc = f" - {t.description}" if t.description else ""
            print(f"ID {t.id}: {status} {t.title}{desc}")
        print("------------------\n")
    finally:
        session.close()

def mark_todo_complete(user_id, todo_id):
    """Updates a todo item's status to completed (verifying ownership)."""
    session = Session()
    try:
        todo = session.query(Todo).filter_by(id=todo_id, user_id=user_id).first()
        if todo:
            todo.completed = True
            session.commit()
            print(f"[*] Todo '{todo.title}' marked as complete.")
        else:
            print(f"[!] Todo ID {todo_id} not found or you don't have permission.")
    except Exception as e:
        session.rollback()
        print(f"[!] Error updating todo: {e}")
    finally:
        session.close()

def delete_todo(user_id, todo_id):
    """Deletes a specific todo item (verifying ownership)."""
    session = Session()
    try:
        todo = session.query(Todo).filter_by(id=todo_id, user_id=user_id).first()
        if todo:
            session.delete(todo)
            session.commit()
            print(f"[*] Todo '{todo.title}' deleted.")
        else:
            print(f"[!] Todo ID {todo_id} not found or you don't have permission.")
    except Exception as e:
        session.rollback()
        print(f"[!] Error deleting todo: {e}")
    finally:
        session.close()

def delete_user(user_id):
    """Deletes a user. Due to cascade setup, all their todos will also be deleted."""
    session = Session()
    try:
        user = session.query(User).get(user_id)
        if user:
            session.delete(user)
            session.commit()
            print(f"[*] Account and all associated todos deleted.")
    except Exception as e:
        session.rollback()
        print(f"[!] Error deleting account: {e}")
    finally:
        session.close()


# =====================================================================
# 5. INTERACTIVE CLI MENU
# =====================================================================

def todo_menu(user_id):
    while True:
        print("\n=== TODO MENU ===")
        print("1. View my Todos")
        print("2. Add a Todo")
        print("3. Mark Todo as Complete")
        print("4. Delete a Todo")
        print("5. Delete my Account")
        print("6. Logout")
        
        choice = input("Select an option (1-6): ").strip()
        
        if choice == '1':
            list_todos(user_id)
        elif choice == '2':
            title = input("Enter todo title: ").strip()
            if title:
                desc = input("Enter description (optional): ").strip()
                create_todo(user_id, title, desc)
            else:
                print("[!] Title cannot be empty.")
        elif choice == '3':
            try:
                todo_id = int(input("Enter Todo ID to complete: ").strip())
                mark_todo_complete(user_id, todo_id)
            except ValueError:
                print("[!] Please enter a valid number.")
        elif choice == '4':
            try:
                todo_id = int(input("Enter Todo ID to delete: ").strip())
                delete_todo(user_id, todo_id)
            except ValueError:
                print("[!] Please enter a valid number.")
        elif choice == '5':
            confirm = input("Are you sure? This will delete all your todos! (y/n): ").strip().lower()
            if confirm == 'y':
                delete_user(user_id)
                break
        elif choice == '6':
            print("Logging out...")
            break
        else:
            print("[!] Invalid option. Try again.")

def main_menu():
    print("Welcome to the Mini Project Todo App!")
    while True:
        print("\n=== START MENU ===")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        
        choice = input("Select an option (1-3): ").strip()
        
        if choice == '1':
            print("\n-- Login --")
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            user_id = authenticate_user(username, password)
            if user_id:
                todo_menu(user_id)
                
        elif choice == '2':
            print("\n-- Register --")
            username = input("Username: ").strip()
            email = input("Email: ").strip()
            password = input("Password: ").strip()
            if username and email and password:
                register_user(username, email, password)
            else:
                print("[!] All fields are required.")
                
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("[!] Invalid option. Try again.")

if __name__ == "__main__":
    main_menu()