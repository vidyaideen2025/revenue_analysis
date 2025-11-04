"""
Model registry for Alembic migrations.

Import all models here so Alembic can detect them for autogenerate.
This file is only imported by Alembic, not by the application code.
"""

from app.core.database import Base  # noqa: F401

# Import all your models here for Alembic autogenerate
# Example:
# from app.models.user import User  # noqa: F401
# from app.models.product import Product  # noqa: F401
# from app.models.order import Order  # noqa: F401

# When you create a new model:
# 1. Create the model file in app/models/
# 2. Import it here
# 3. Run: alembic revision --autogenerate -m "Add your_model"
# 4. Run: alembic upgrade head
