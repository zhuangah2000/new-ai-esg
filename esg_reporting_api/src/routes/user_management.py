from flask import Blueprint, request, jsonify
from src.models.esg_models import db, User, Role
from datetime import datetime

user_management_bp = Blueprint("user_management", __name__)

# Helper function to check if user has admin role
def is_admin(user_id):
    user = User.query.get(user_id)
    if user and user.role and user.role.name == "admin":
        return True
    return False

# User Management Routes
@user_management_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    # In a real app, you would hash the password here
    # data["password_hash"] = generate_password_hash(data["password"])
    try:
        # Ensure role exists
        role = Role.query.get(data["role_id"])
        if not role:
            return jsonify({"success": False, "error": "Role not found"}), 404

        new_user = User(
            username=data["username"],
            email=data["email"],
            role_id=data["role_id"]
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": True, "data": new_user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@user_management_bp.route("/users", methods=["GET"])
def get_users():
    try:
        users = User.query.all()
        return jsonify({"success": True, "data": [u.to_dict() for u in users]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@user_management_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)
        if "role_id" in data:
            role = Role.query.get(data["role_id"])
            if not role:
                return jsonify({"success": False, "error": "Role not found"}), 404
            user.role_id = data["role_id"]

        db.session.commit()
        return jsonify({"success": True, "data": user.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@user_management_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": True, "message": "User deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# Role Management Routes
@user_management_bp.route("/roles", methods=["POST"])
def create_role():
    data = request.get_json()
    try:
        new_role = Role(
            name=data["name"],
            description=data.get("description"),
            permissions=data.get("permissions") # This would typically be a JSON string
        )
        db.session.add(new_role)
        db.session.commit()
        return jsonify({"success": True, "data": new_role.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@user_management_bp.route("/roles", methods=["GET"])
def get_roles():
    try:
        roles = Role.query.all()
        return jsonify({"success": True, "data": [r.to_dict() for r in roles]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@user_management_bp.route("/roles/<int:role_id>", methods=["PUT"])
def update_role(role_id):
    data = request.get_json()
    try:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({"success": False, "error": "Role not found"}), 404
        
        role.name = data.get("name", role.name)
        role.description = data.get("description", role.description)
        role.permissions = data.get("permissions", role.permissions)
        
        db.session.commit()
        return jsonify({"success": True, "data": role.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@user_management_bp.route("/roles/<int:role_id>", methods=["DELETE"])
def delete_role(role_id):
    try:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({"success": False, "error": "Role not found"}), 404
        
        # Prevent deleting roles that have associated users
        if User.query.filter_by(role_id=role_id).first():
            return jsonify({"success": False, "error": "Cannot delete role with associated users"}), 400

        db.session.delete(role)
        db.session.commit()
        return jsonify({"success": True, "message": "Role deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


