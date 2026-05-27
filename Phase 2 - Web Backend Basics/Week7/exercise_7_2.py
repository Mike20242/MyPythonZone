from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine('sqlite:///exercise_7_2.db', echo=False)
Base = declarative_base()

# 1. USER MODEL
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    
    # 2. RELATIONSHIP DEFINITION
    # relationship() establishes a link between the User and Post objects.
    # 'Post' is the name of the class we are relating to.
    # back_populates='author' tells SQLAlchemy that the 'author' attribute
    # in the Post class will be the reverse of this relationship.
    # This means user.posts will return a list of Post objects,
    # and post.author will return the User object.
    posts = relationship('Post', back_populates='author')

    def __repr__(self):
        return f"<User('{self.username}')>"

# 3. POST MODEL
class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(String(500))
    
    # 4. FOREIGN KEY
    # ForeignKey specifies that this column contains values that match
    # the 'id' column in the 'users' table. It represents the "Many" side
    # of the One-to-Many relationship (One User has Many Posts).
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Reverse relationship linking back to the User.
    author = relationship('User', back_populates='posts')

    def __repr__(self):
        return f"<Post('{self.title}')>"

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def demonstrate_relationship():
    # Clean up for clean run
    session.query(Post).delete()
    session.query(User).delete()
    session.commit()

    print("\n--- DEMONSTRATING ONE-TO-MANY RELATIONSHIP ---\n")

    # Create a user
    user = User(username='alice')
    
    # Create posts. Notice we don't explicitly need to set user_id.
    # We can just append to the 'posts' relationship collection.
    post1 = Post(title='My first post', content='Hello world!')
    post2 = Post(title='SQLAlchemy is great', content='Learning relationships.')
    
    # Add posts to the user's posts list
    user.posts.append(post1)
    user.posts.append(post2)
    
    # Add the user to the session. 
    # Because of the relationship, SQLAlchemy is smart enough to also add the posts!
    session.add(user)
    session.commit()
    
    print(f"Created user: {user.username}")
    print(f"Created posts for {user.username}:")
    for post in user.posts:
        print(f" - {post.title}")
        
    print("\nNow querying from the Post perspective...")
    # Query the post and see its author
    queried_post = session.query(Post).filter_by(title='My first post').first()
    print(f"Post '{queried_post.title}' was written by: {queried_post.author.username}")
    print("\n--- END OF DEMONSTRATION ---")

if __name__ == '__main__':
    demonstrate_relationship()
