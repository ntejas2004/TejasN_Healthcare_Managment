"""
seed_users.py — Creates 3 demo users for the new RBAC roles.
Run once: python seed_users.py  (from the backend/ folder)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, engine
import models
from auth import hash_password

models.Base.metadata.create_all(bind=engine)

DEMO_USERS = [
    {"username": "admin",    "email": "admin@healthcare.local",   "password": "admin123",    "role": "administrator"},
    {"username": "clinops",  "email": "clinops@healthcare.local", "password": "clinops123",  "role": "clinical_operations"},
    {"username": "analyst",  "email": "analyst@healthcare.local", "password": "analyst123",  "role": "analyst"},
]

db = SessionLocal()
try:
    for u in DEMO_USERS:
        existing = db.query(models.User).filter(models.User.username == u["username"]).first()
        if existing:
            # Update role in case it changed from a previous seed
            existing.role = u["role"]
            existing.hashed_password = hash_password(u["password"])
            print(f"  [updated] User '{u['username']}' -> role '{u['role']}'")
        else:
            user = models.User(
                username=u["username"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
                is_active=True,
            )
            db.add(user)
            print(f"  [created] User '{u['username']}' with role '{u['role']}'")
    db.commit()
    print("\nDone! Demo users are ready.")
    print("  admin    / admin123   -> Administrator  (full access)")
    print("  clinops  / clinops123 -> Clinical Operations (read + write, no delete)")
    print("  analyst  / analyst123 -> Analyst (analytics only)")
finally:
    db.close()
