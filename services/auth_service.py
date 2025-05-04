from datetime import datetime
from flask_jwt_extended import create_access_token
from models import db
from models.user import User
from models.supplier import Supplier
from models.logs import Log
import re

class AuthService:
    @staticmethod
    def register_user(username, email, password, role, supplier_id=None):
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {"success": False, "message": "Invalid email format"}

        if User.query.filter_by(username=username).first():
            return {"success": False, "message": "Username already exists"}

        if User.query.filter_by(email=email).first():
            return {"success": False, "message": "Email already exists"}

        if role == 'supplier':
            if not supplier_id:
                return {"success": False, "message": "Supplier ID is required for supplier role"}
            supplier = Supplier.query.filter_by(supplier_id=supplier_id).first()
            if not supplier:
                return {"success": False, "message": "Invalid Supplier ID"}
            if User.query.filter_by(supplier_id=supplier_id).first():
                return {"success": False, "message": "Supplier ID already registered"}

        new_user = User(
            username=username,
            email=email,
            role=role,
            supplier_id=supplier_id if role == 'supplier' else None
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()

            log = Log(
                user_id=new_user.id,
                module="authentication",
                action="user_registration",
                description=f"User {username} registered with role {role}",
                status="success"
            )
            db.session.add(log)
            db.session.commit()

            return {"success": True, "message": "User registered successfully", "user_id": new_user.id}
        except Exception as e:
            db.session.rollback()
            log = Log(
                module="authentication",
                action="user_registration",
                description=f"Failed to register user {username}: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            return {"success": False, "message": "Registration failed due to internal error"}

    @staticmethod
    def login_user(username, password):
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            log = Log(
                module="authentication",
                action="user_login",
                description=f"Failed login attempt for username {username}",
                status="warning"
            )
            db.session.add(log)
            db.session.commit()
            return {"success": False, "message": "Invalid username or password"}

        if not user.is_active:
            log = Log(
                user_id=user.id,
                module="authentication",
                action="user_login",
                description=f"Login attempt by inactive user {username}",
                status="warning"
            )
            db.session.add(log)
            db.session.commit()
            return {"success": False, "message": "Account is inactive"}

        user.last_login = datetime.utcnow()
        db.session.commit()

        access_token = create_access_token(
            identity=str(user.id),

            additional_claims={
                "username": user.username,
                "role": user.role,
                "supplier_id": user.supplier_id
            }
        )

        log = Log(
            user_id=user.id,
            module="authentication",
            action="user_login",
            description=f"User {username} logged in successfully",
            status="success"
        )
        db.session.add(log)
        db.session.commit()

        return {
            "success": True,
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "supplier_id": user.supplier_id
            }
        }
