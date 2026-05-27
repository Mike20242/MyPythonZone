from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('sqlite:///exercise_7_3.db', echo=False)
Base = declarative_base()

class Product(Base):
    """
    We'll use a Product model to demonstrate filtering and ordering based on price and name.
    """
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    price = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Product('{self.name}', Category='{self.category}', Price=${self.price})>"

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def seed_data():
    session.query(Product).delete()
    products = [
        Product(name='Laptop', category='Electronics', price=1200),
        Product(name='Mouse', category='Electronics', price=25),
        Product(name='Keyboard', category='Electronics', price=75),
        Product(name='Desk', category='Furniture', price=300),
        Product(name='Chair', category='Furniture', price=150),
        Product(name='Monitor', category='Electronics', price=200)
    ]
    session.add_all(products)
    session.commit()

def demonstrate_queries():
    seed_data()
    print("\n--- DEMONSTRATING QUERY FILTERS AND ORDER_BY ---\n")

    # ==========================================
    # 1. FILTERING (filter and filter_by)
    # ==========================================
    print("1. Filtering with filter_by (Simple equality)")
    # filter_by uses keyword arguments. It's simple but limited to equality.
    electronics = session.query(Product).filter_by(category='Electronics').all()
    for item in electronics:
        print(f" - {item}")

    print("\n2. Filtering with filter (Complex conditions)")
    # filter uses Python expressions (==, >, <, !=, etc.) with the Model's column attributes.
    expensive_items = session.query(Product).filter(Product.price >= 200).all()
    for item in expensive_items:
        print(f" - {item}")
        
    print("\n3. Combining filters (AND condition)")
    # You can chain .filter() calls or pass multiple arguments
    expensive_electronics = session.query(Product).filter(
        Product.category == 'Electronics',
        Product.price > 100
    ).all()
    for item in expensive_electronics:
        print(f" - {item}")

    # ==========================================
    # 2. ORDERING (order_by)
    # ==========================================
    print("\n4. Ordering Results (Ascending)")
    # By default, order_by sorts in ascending order
    cheapest_first = session.query(Product).order_by(Product.price).all()
    for item in cheapest_first:
        print(f" - {item}")

    print("\n5. Ordering Results (Descending)")
    # We can use .desc() on the column attribute to sort descending
    most_expensive_first = session.query(Product).order_by(Product.price.desc()).all()
    for item in most_expensive_first:
        print(f" - {item}")
        
    print("\n6. Combining Filter and Order By")
    # You can chain them together. Here we get Electronics ordered by price descending.
    ordered_electronics = session.query(Product)\
        .filter(Product.category == 'Electronics')\
        .order_by(Product.price.desc())\
        .all()
    for item in ordered_electronics:
        print(f" - {item}")

    print("\n--- END OF DEMONSTRATION ---")

if __name__ == '__main__':
    demonstrate_queries()
