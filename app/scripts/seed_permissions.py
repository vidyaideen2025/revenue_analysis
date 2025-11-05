"""Seed script to populate permissions and roles in the database."""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.models.permission import Permission, Role, SYSTEM_PERMISSIONS, SYSTEM_ROLES


async def seed_permissions_and_roles():
    """Seed system permissions and roles."""
    
    async with async_session_maker() as db:
        try:
            print("🌱 Starting permission and role seeding...")
            
            # Create permissions
            print("\n📝 Creating permissions...")
            permission_map = {}
            
            for code, perm_data in SYSTEM_PERMISSIONS.items():
                # Check if permission already exists
                from sqlalchemy import select
                result = await db.execute(
                    select(Permission).where(Permission.code == code)
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    print(f"  ⏭️  Permission '{code}' already exists, skipping...")
                    permission_map[code] = existing
                else:
                    permission = Permission(
                        code=code,
                        name=perm_data["name"],
                        description=perm_data["description"],
                        category=perm_data["category"].value,
                        action=perm_data["action"].value,
                        resource=perm_data["resource"],
                        is_active=True
                    )
                    db.add(permission)
                    permission_map[code] = permission
                    print(f"  ✅ Created permission: {code}")
            
            await db.commit()
            print(f"\n✅ Created {len(SYSTEM_PERMISSIONS)} permissions")
            
            # Refresh permissions to get IDs
            for perm in permission_map.values():
                await db.refresh(perm)
            
            # Create roles with permissions
            print("\n👥 Creating roles...")
            
            for role_code, role_data in SYSTEM_ROLES.items():
                # Check if role already exists
                from sqlalchemy import select
                result = await db.execute(
                    select(Role).where(Role.code == role_code)
                )
                existing_role = result.scalar_one_or_none()
                
                if existing_role:
                    print(f"  ⏭️  Role '{role_code}' already exists, updating permissions...")
                    # Update permissions for existing role
                    existing_role.permissions = [
                        permission_map[perm_code]
                        for perm_code in role_data["permissions"]
                        if perm_code in permission_map
                    ]
                    print(f"  ✅ Updated role: {role_code} with {len(existing_role.permissions)} permissions")
                else:
                    role = Role(
                        code=role_code,
                        name=role_data["name"],
                        description=role_data["description"],
                        is_system_role=True,
                        is_active=True
                    )
                    
                    # Add permissions to role
                    role.permissions = [
                        permission_map[perm_code]
                        for perm_code in role_data["permissions"]
                        if perm_code in permission_map
                    ]
                    
                    db.add(role)
                    print(f"  ✅ Created role: {role_code} with {len(role.permissions)} permissions")
            
            await db.commit()
            print(f"\n✅ Created/Updated {len(SYSTEM_ROLES)} roles")
            
            # Print summary
            print("\n" + "="*60)
            print("📊 SEEDING SUMMARY")
            print("="*60)
            
            for role_code, role_data in SYSTEM_ROLES.items():
                print(f"\n{role_code} ({role_data['name']}):")
                print(f"  Description: {role_data['description']}")
                print(f"  Permissions: {len(role_data['permissions'])}")
                print("  Categories:")
                
                categories = {}
                for perm_code in role_data['permissions']:
                    if perm_code in SYSTEM_PERMISSIONS:
                        category = SYSTEM_PERMISSIONS[perm_code]['category'].value
                        if category not in categories:
                            categories[category] = 0
                        categories[category] += 1
                
                for cat, count in categories.items():
                    print(f"    - {cat}: {count} permissions")
            
            print("\n" + "="*60)
            print("✅ Seeding completed successfully!")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    print("="*60)
    print("🚀 RBAC Permission & Role Seeding Script")
    print("="*60)
    asyncio.run(seed_permissions_and_roles())
