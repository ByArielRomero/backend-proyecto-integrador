import datetime
import jwt
import bcrypt
from flask import Blueprint, Response, g, json, jsonify, request
from flask_cors import CORS
from models import db, Usuario
from controllers.auth import token_required
from dotenv import load_dotenv
import os

load_dotenv()
# Para los que hagan pull: definan esta variable de entorno en un archivo .env
# Esto es temporal hasta que se suba el codigo a un servidor
secret_key = os.getenv("SECRET_KEY")

login_bp = Blueprint('login_bp', __name__)
CORS(login_bp, origins=["http://localhost:3000", "http://127.0.0.1:3000"], supports_credentials=True)


@login_bp.route("/auth/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.status_code = 200
        return response

    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return jsonify({"error": "El usuario y la contraseña son obligatorios"}), 400
        
        usuario = Usuario.query.filter_by(username=username).first()
        
        if not usuario or not bcrypt.checkpw(password.encode(), usuario.password_hash.encode()):
            return jsonify({"error": "Credenciales incorrectas"}), 401
        
        payload = {
            "user_id": usuario.id,
            "username": usuario.username,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        }

        token = jwt.encode(payload, secret_key, algorithm="HS256")

        return jsonify({
            "success": True,
            "message": "Inicio válido",
            "token": token,
            "user": {"id": usuario.id, "username": usuario.username, "role": usuario.role}
        }), 200

    except Exception as e:
        print("Error en login:", e)
        return jsonify({"error": "Error interno del servidor"}), 500
    
@login_bp.route("/usuarios", methods = ["POST"])
def create_user():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        role = data.get("role")
        
        if not username or not password or not role:
            return jsonify({"error": "Todos los campos son obligatorios"}), 400
        
        roles_permitidos = ["admin", "user", "moderator"]
        if role not in roles_permitidos:
            return jsonify({"error": f"Rol no válido. Roles permitidos: {', '.join(roles_permitidos)}"}), 400
        
        if len(password) < 6:
            return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400
        
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        if Usuario.query.filter_by(username=username).first():
            return jsonify({"error": "El usuario ya existe"}), 400

        nuevo_usuario = Usuario(
            username=username,
            password_hash=password_hash.decode('utf-8'),  # guardamos como string
            role=role
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify({"message": "Usuario creado exitosamente"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear usuario: {str(e)}")
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

@login_bp.route("/me", methods=["GET"])
def obtener_usuario_actual():
    usuario = Usuario.query.get(g.user["user_id"])
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "id": usuario.id,
        "username": usuario.username,
        "role": usuario.role
    }), 200

@login_bp.route("/usuarios/<int:user_id>", methods=["PATCH"])
def actualizar_usuario(user_id):
    try:
        data = request.get_json()
        
        current_user = Usuario.query.get(g.user["user_id"])
        if not current_user:
            return jsonify({"error": "Usuario actual no encontrado"}), 404
        
        if current_user.id != user_id and current_user.role != "admin":
            return jsonify({"error": "No tienes permisos para actualizar este usuario"}), 403
        
        usuario = Usuario.query.get(user_id)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        new_username = data.get("username")
        new_password = data.get("password")
        new_role = data.get("role")

        if new_role and current_user.role != "admin":
            return jsonify({"error": "Solo los administradores pueden cambiar roles"}), 403
        
        if new_role:
            roles_permitidos = ["admin", "user", "moderator"]
            if new_role not in roles_permitidos:
                return jsonify({"error": f"Rol no válido. Roles permitidos: {', '.join(roles_permitidos)}"}), 400

        if new_username:
            if Usuario.query.filter(Usuario.username==new_username, Usuario.id != user_id).first():
                return jsonify({"error": "El nombre de usuario ya está en uso"}), 400
            usuario.username = new_username
        
        if new_password:
            if len(new_password) < 6:
                return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400
            usuario.password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode('utf-8')
        
        if new_role:
            usuario.role = new_role

        if not new_username and not new_password and not new_role:
            return jsonify({"error": "No se dieron datos para actualizar"}), 400

        db.session.commit()

        new_payload = {
            "user_id": usuario.id,
            "username": usuario.username,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)  # token válido 1 hora
        }

        new_token = jwt.encode(new_payload, secret_key, algorithm="HS256")

        return jsonify({"message": "Usuario actualizado exitosamente", "new_token": new_token}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor"}), 500

@login_bp.route("/usuarios/<int:id>", methods=["GET"])
def get_user_data_by_id(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
        
    return jsonify({
        "id": usuario.id,
        "username": usuario.username,
        "role": usuario.role
    }), 200  


@login_bp.route("/usuarios/<int:id>", methods=["DELETE"])
def delete_user_by_id(id):
    usuario = Usuario.query.get(id)
    
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    db.session.delete(usuario)
    db.session.commit()

    return jsonify({"message": "Usuario eliminado exitosamente"}), 200


@login_bp.route("/usuarios", methods=["GET"])
def get_all_users():
    try:
        usuarios = Usuario.query.all()

        if not usuarios:
            return jsonify({"message": "No hay usuarios registrados"}), 404

        lista = [
            {
                "id": usuario.id,
                "username": usuario.username,
                "role": usuario.role
            }
            for usuario in usuarios
        ]

        return jsonify(lista), 200
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500