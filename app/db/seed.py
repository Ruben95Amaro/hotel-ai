"""
Database seeding utilities.
Creates initial admin user and other required data.
"""
import uuid
from datetime import datetime

from app.db.repositories import UserRepository
from app.db.models import User
from app.settings.config import get_settings


def hash_password(password: str) -> str:
    """Hash password using SHA-256 (same as auth module)."""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


async def create_admin_user(user_repo: UserRepository) -> User:
    """
    Create the default admin user if it doesn't exist.
    
    Returns:
        The admin user (existing or newly created).
    """
    settings = get_settings()
    
    # Admin credentials - can be overridden via environment variables
    admin_email = getattr(settings, 'admin_email', 'admin@grandoceanhotel.com')
    admin_password = getattr(settings, 'admin_password', 'AdminPass123')
    admin_name = getattr(settings, 'admin_name', 'Hotel Administrator')
    
    # Check if admin already exists
    existing_admin = await user_repo.get_by_email(admin_email)
    if existing_admin:
        # Ensure it's an admin
        if not existing_admin.is_admin:
            existing_admin.is_admin = True
            existing_admin.updated_at = datetime.utcnow()
            await user_repo.update(existing_admin)
        return existing_admin
    
    # Create new admin user
    admin_user = User(
        id=str(uuid.uuid4()),
        email=admin_email,
        full_name=admin_name,
        phone="",
        password_hash=hash_password(admin_password),
        is_admin=True,
        is_active=True,
        preferences={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    created = await user_repo.create(admin_user)
    print(f"✅ Created admin user: {admin_email} (ID: {created.id})")
    print(f"   Password: {admin_password}")
    print(f"   Please change this password after first login!")
    
    return created


async def seed_database(user_repo: UserRepository) -> None:
    """
    Seed the database with initial data.
    Currently creates admin user only.
    """
    print("🌱 Seeding database...")
    await create_admin_user(user_repo)
    print("✅ Database seeding complete!")


if __name__ == "__main__":
    # Allow running as standalone script for testing
    import asyncio
    from app.di import get_container
    
    async def main():
        container = get_container()
        await container.initialize()
        await seed_database(container.user_repository)
        await container.close()
    
    asyncio.run(main())