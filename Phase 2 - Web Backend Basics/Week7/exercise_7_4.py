from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine('sqlite:///exercise_7_4.db', echo=False)
Base = declarative_base()

class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    
    # 1. CASCADE CONFIGURATION
    # The 'cascade' parameter defines how operations performed on the "Parent" (Department)
    # propagate to the "Children" (Employees).
    # 'all' means all operations (save, merge, expunge, delete) should cascade.
    # 'delete-orphan' means that if an Employee is removed from the department.employees
    # collection, or if the parent Department is deleted, the orphaned Employee record
    # should be DELETED from the database entirely.
    employees = relationship(
        'Employee', 
        back_populates='department',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Department('{self.name}')>"

class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    
    # ForeignKey linking to the Department
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    
    department = relationship('Department', back_populates='employees')

    def __repr__(self):
        return f"<Employee('{self.name}')>"

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def demonstrate_cascade_delete():
    # Clean up for clean run
    session.query(Employee).delete()
    session.query(Department).delete()
    session.commit()

    print("\n--- DEMONSTRATING CASCADE DELETE ---\n")

    # 1. Create a Department with Employees
    hr = Department(name='HR')
    hr.employees = [
        Employee(name='Alice'),
        Employee(name='Bob')
    ]
    
    session.add(hr)
    session.commit()
    
    print("Initial State:")
    print("Departments:", session.query(Department).all())
    print("Employees:", session.query(Employee).all())
    
    # 2. Delete the Department
    print("\nAction: Deleting the 'HR' Department...")
    session.delete(hr)
    session.commit()
    
    # 3. Verify that the Employees were also deleted (Cascade)
    print("\nState after Deletion:")
    print("Departments:", session.query(Department).all())
    
    # Notice that Alice and Bob are gone! The cascade='all, delete-orphan' 
    # told SQLAlchemy to automatically delete them when their parent was deleted.
    print("Employees:", session.query(Employee).all()) 

    print("\n--- END OF DEMONSTRATION ---")

if __name__ == '__main__':
    demonstrate_cascade_delete()
