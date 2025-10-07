import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our models
sys.path.append(str(Path(__file__).parent))

from models.database import Base, engine, SessionLocal, User, UserRole
from app.utils import get_password_hash

def init_db():
    """Initialize the database with required tables and an admin user."""
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin = db.query(User).filter(User.email == admin_email).first()
        
        if not admin:
            # Create admin user
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash(admin_password),
                full_name="Admin User",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print(f"Created admin user with email: {admin_email}")
        else:
            print(f"Admin user already exists with email: {admin_email}")
            
        print("Database initialization complete!")
        
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
        sys.exit(1)
        
    finally:
        db.close()

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Initialize the database
    init_db()
