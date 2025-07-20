#!/usr/bin/env python3
"""
Script to create an admin user for Elimu Hub.
Usage: python scripts/create_admin.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.auth.models import User
from app.auth.utils import get_password_hash
from app.utils.logger import logger

def create_admin_user(email: str, username: str, password: str):
    """Create an admin user."""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            if existing_user.email == email:
                logger.error(f"User with email {email} already exists")
                return False
            else:
                logger.error(f"User with username {username} already exists")
                return False
        
        # Create admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            is_admin=True,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        logger.info(f"Admin user created successfully: {email}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating admin user: {e}")
        return False
    finally:
        db.close()

def main():
    """Main function to create admin user interactively."""
    print("Elimu Hub - Admin User Creation")
    print("=" * 40)
    
    email = input("Enter admin email: ").strip()
    username = input("Enter admin username: ").strip()
    password = input("Enter admin password: ").strip()
    
    if not email or not username or not password:
        print("Error: All fields are required")
        return
    
    if len(password) < 8:
        print("Error: Password must be at least 8 characters long")
        return
    
    success = create_admin_user(email, username, password)
    
    if success:
        print(f"\n✅ Admin user created successfully!")
        print(f"Email: {email}")
        print(f"Username: {username}")
        print("\nYou can now login using these credentials.")
    else:
        print("\n❌ Failed to create admin user. Check the logs for details.")

if __name__ == "__main__":
    main() 