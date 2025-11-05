"""Seed initial admin users into the database."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.crud.user import user_repo
from app.crud.department import department_repo
from app.schemas.user import UserCreate
from app.models.user import UserRole


async def seed_admin_users():
    """Create initial admin users if they don't exist."""
    
    async with AsyncSessionLocal() as db:
        # Get IT department (or create if doesn't exist)
        it_dept = await department_repo.get_by_code(db, "IT")
        if not it_dept:
            print("⚠️  IT department not found. Please create departments first.")
            print("Run: python scripts/seed_departments.py")
            return
        
        admin_users = [
            {
                "email": "admin@revenueguardian.com",
                "username": "admin",
                "password": "Admin@123",
                "full_name": "Primary Administrator",
                "department_id": it_dept.id,
                "role": UserRole.ADMIN.value
            },
            {
                "email": "superadmin@revenueguardian.com",
                "username": "superadmin",
                "password": "Super@123",
                "full_name": "Super Administrator",
                "department_id": it_dept.id,
                "role": UserRole.ADMIN.value
            },
            {
                "email": "sysadmin@revenueguardian.com",
                "username": "sysadmin",
                "password": "SysAdmin@123",
                "full_name": "System Administrator",
                "department_id": it_dept.id,
                "role": UserRole.ADMIN.value
            },
        ]
        
        for user_data in admin_users:
            # Check if user already exists
            existing_user = await user_repo.get_by_email(db, user_data["email"])
            
            if existing_user:
                print(f"✓ User {user_data['email']} already exists, skipping...")
                continue
            
            # Create user
            user_create = UserCreate(**user_data)
            created_user = await user_repo.create(db, user_create)
            
            print(f"✓ Created admin user: {created_user.email} (username: {created_user.username})")
    
    print("\n✅ Admin user seeding completed!")
    print("\nYou can now login with:")
    print("  - admin@revenueguardian.com / Admin@123")
    print("  - superadmin@revenueguardian.com / Super@123")
    print("  - sysadmin@revenueguardian.com / SysAdmin@123")


if __name__ == "__main__":
    print("🌱 Seeding admin users...\n")
    asyncio.run(seed_admin_users())
