"""Seed initial departments into the database."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import AsyncSessionLocal
from app.models.user import User  # Import to register model before Department relationship
from app.crud.department import department_repo
from app.schemas.department import DepartmentCreate


async def seed_departments():
    """Create initial departments if they don't exist."""
    
    departments = [
        {
            "name": "Information Technology",
            "code": "IT",
            "description": "IT and system administration department"
        },
        {
            "name": "Finance",
            "code": "FINANCE",
            "description": "Financial management and accounting department"
        },
        {
            "name": "Operations",
            "code": "OPERATIONS",
            "description": "Operations and reconciliation department"
        },
        {
            "name": "Executive",
            "code": "EXECUTIVE",
            "description": "Executive and management department"
        },
        {
            "name": "Human Resources",
            "code": "HR",
            "description": "Human resources department"
        },
        {
            "name": "Legal",
            "code": "LEGAL",
            "description": "Legal and compliance department"
        },
    ]
    
    async with AsyncSessionLocal() as db:
        print("🌱 Seeding departments...\n")
        
        for dept_data in departments:
            # Check if department already exists
            existing_dept = await department_repo.get_by_code(db, dept_data["code"])
            
            if existing_dept:
                print(f"✓ Department '{dept_data['code']}' already exists, skipping...")
                continue
            
            # Create department
            dept_create = DepartmentCreate(**dept_data)
            created_dept = await department_repo.create(db, dept_create)
            
            print(f"✓ Created department: {created_dept.name} ({created_dept.code})")
        
        print("\n✅ Department seeding completed!")
        print(f"\nCreated {len(departments)} departments:")
        for dept in departments:
            print(f"  - {dept['code']}: {dept['name']}")


if __name__ == "__main__":
    asyncio.run(seed_departments())
