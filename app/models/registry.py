"""
Model registry for Alembic migrations.

Import all models here so Alembic can detect them for autogenerate.
This file is only imported by Alembic, not by the application code.
"""

from app.core.database import Base  # noqa: F401

# Import all your models here for Alembic autogenerate
from app.models.user import User  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.department import Department  # noqa: F401
from app.models.permission import Permission, Role  # noqa: F401

# Add more models as you create them:
#
