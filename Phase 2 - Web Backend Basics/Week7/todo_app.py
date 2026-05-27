from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os

# =====================================================================
# MINI PROJECT: TODO APP BACKEND WITH DATABASE
# =====================================================================

# 1. Database Setup
# Using SQLite for a simple, file-based database.
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

    # Primary key
    id = Column(Integer, primary_key=True)
    
    # User details
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False) # In a real app, this MUST be hashed!

    # One-to-Many relationship with Todo
    # A user can have many todos. If the user is deleted, their todos are deleted too (cascade='all, delete-orphan')
    todos = relationship('Todo', back_populates='owner', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User('{self.username}')>"


class Todo(Base):
    """
    Todo model representing a task that belongs to a specific User.
    """
    __tablename__ = 'todos'

    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Task details
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
# 3. APPLICATION LOGIC / CRUD FUNCTIONS
# =====================================================================

def create_user(username, email, password):
    """Creates a new user and saves it to the database."""
    session = Session()
    try:
        new_user = User(username=username, email=email, password=password)
        session.add(new_user)
        session.commit()
        print(f"[*] User '{username}' created successfully.")
        return new_user.id
    except Exception as e:
        session.rollback()
        print(f"[!] Error creating user: {e}")
    finally:
        session.close()

def create_todo(user_id, title, description=""):
    """Creates a new todo item for a specific user."""
    session = Session()
    try:
        new_todo = Todo(title=title, description=description, user_id=user_id)
        session.add(new_todo)
        session.commit()
        print(f"[*] Todo '{title}' added for user ID {user_id}.")
        return new_todo.id
    except Exception as e:
        session.rollback()
        print(f"[!] Error creating todo: {e}")
    finally:
        session.close()

def get_user_todos(user_id):
    """Retrieves all todos for a specific user, ordering by completion status."""
    session = Session()
    try:
        # We query Todos, filter by the correct user_id, 
        # and order so that pending tasks show up before completed tasks.
        todos = session.query(Todo).filter_by(user_id=user_id).order_by(Todo.completed).all()
        
        user = session.query(User).get(user_id)
        if user:
            print(f"\n--- Todos for {user.username} ---")
            if not todos:
                print("  No todos yet.")
            for t in todos:
                status = "[x]" if t.completed else "[ ]"
                print(f"  {status} {t.id}: {t.title} - {t.description}")
            print("---------------------------\n")
        return todos
    finally:
        session.close()

def mark_todo_complete(todo_id):
    """Updates a todo item's status to completed."""
    session = Session()
    try:
        todo = session.query(Todo).get(todo_id)
        if todo:
            todo.completed = True
            session.commit()
            print(f"[*] Marked todo {todo_id} as complete.")
        else:
            print(f"[!] Todo {todo_id} not found.")
    except Exception as e:
        session.rollback()
        print(f"[!] Error updating todo: {e}")
    finally:
        session.close()

def delete_user(user_id):
    """Deletes a user. Due to cascade setup, all their todos will also be deleted."""
    session = Session()
    try:
        user = session.query(User).get(user_id)
        if user:
            username = user.username
            session.delete(user)
            session.commit()
            print(f"[*] User '{username}' and all their todos were deleted.")
        else:
            print(f"[!] User {user_id} not found.")
    except Exception as e:
        session.rollback()
        print(f"[!] Error deleting user: {e}")
    finally:
        session.close()


# =====================================================================
# 4. DEMONSTRATION SCRIPT
# =====================================================================

def run_demo():
    print("=== TODO APP DEMO START ===")
    
    # 1. Create a user
    user_id = create_user("giabao", "giabao@example.com", "securepassword123")
    
    if user_id:
        # 2. Add some todos for the user
        todo1_id = create_todo(user_id, "Learn SQLAlchemy", "Understand ORM concepts and relationships.")
        todo2_id = create_todo(user_id, "Do Exercise 7.4", "Implement cascade delete.")
        todo3_id = create_todo(user_id, "Buy groceries", "Milk, eggs, bread")

        # 3. View the todos (Read)
        get_user_todos(user_id)

        # 4. Complete a task (Update)
        mark_todo_complete(todo1_id)
        
        # View again to see the updated status
        get_user_todos(user_id)

        # 5. Delete the user (Delete with Cascade)
        # Deleting the user will automatically delete all their todos 
        # because of cascade='all, delete-orphan' in the User model.
        delete_user(user_id)
        
        # Verify deletion
        print("\nChecking if any todos remain in database for this user...")
        session = Session()
        remaining_todos = session.query(Todo).filter_by(user_id=user_id).all()
        print(f"Remaining todos count: {len(remaining_todos)}")
        session.close()

    print("=== TODO APP DEMO END ===")


if __name__ == "__main__":
    # Remove existing db to start fresh for the demo
    if os.path.exists(db_path):
        os.remove(db_path)
    
    run_demo()
