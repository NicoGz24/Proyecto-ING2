from os import path, environ
from flask import Flask, render_template, g, Blueprint
from flask_session import Session
from config import config
from app import db
from app.helpers import handler
from app.helpers import auth as helper_auth
from app.resources import auth
from app.resources import user
from app.resources import turn

def create_app(environment="development"):
    # Configuración inicial de la app
    app = Flask(__name__)

    app.config["SESSION_PERMANENT"] = False

    # Carga de la configuración
    env = environ.get("FLASK_ENV", environment)
    app.config.from_object(config[env])

    # Server Side session
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    # Configure db
    db.init_app(app)


    # Funciones que se exportan al contexto de Jinja2
    app.jinja_env.globals.update(is_authenticated=helper_auth.authenticated)

    # Modulo de authenticacion 
    app.add_url_rule("/iniciar-sesion", "login", auth.login, methods=["GET", "POST"]) 
    app.add_url_rule("/cerrar-sesion", "logout", auth.logout, methods=["GET"]) 

    # Modulo de usuarios
    app.add_url_rule("/registro", "user_register", user.user_register, methods=["GET", "POST"])
    app.add_url_rule("/perfil-del-usuario", "user_profile", user.user_profile)
    app.add_url_rule("/editar-perfil-del-usuario", "edit_user_profile", user.edit_user_profile, methods=["GET", "POST"])
    app.add_url_rule("/usuario-comun/<string:success>", "common_user", user.common_user) 
    app.add_url_rule("/usuario-enfermero", "nurse_user", user.nurse_user)
    app.add_url_rule("/perfil-del-usuario-enfermero/<int:id_nurse>", "nurse_profile", user.nurse_profile)
    
    
    
    # Modulo de turnos
    app.add_url_rule("/solicitar-turno", "add_turn", turn.add_turn, methods=["POST"])
    app.add_url_rule("/confirmar-turno/<int:turn_id>", "confirm_turn", turn.confirm_turn, methods=["GET", "POST"])
    app.add_url_rule("/cancelar-turno/<int:turn_id>", "cancel_turn", turn.cancel_turn, methods=["GET"])
    app.add_url_rule("/cancelar-turno-enfermero/<int:turn_id>", "nurse_cancel_turn", turn.nurse_cancel_turn, methods=["GET"])
    app.add_url_rule("/descargar-certificado/<int:turn_id>", "download_certificate_turn", turn.download_certificate_turn, methods=["GET"])
    app.add_url_rule("/detalles-paciente/<int:patient_id>", "patient_details", turn.patient_details) 
    
    #Modulo de administrador
    app.add_url_rule("/manejo-de-enfermeros", "nurses_management", user.nurses_management)
    app.add_url_rule("/registro-enfermero", "nurse_register", user.nurse_register, methods=["POST"])
    app.add_url_rule("/reportes", "admin_reports", turn.admin_reports, methods=["GET", "POST"])
    app.add_url_rule("/turnos-fiebre-amarilla", "admin_yellow_fever_turns", turn.admin_yellow_fever_turns)
    app.add_url_rule("/cancelar-turno-admin/<int:turn_id>", "admin_cancel_turn", turn.admin_cancel_turn, methods=["GET"]) 
    app.add_url_rule("/confirmar-turno-admin/<int:turn_id>", "admin_confirm_turn", turn.admin_confirm_turn, methods=["GET"])
    

    app.add_url_rule("/editar-perfil-enfermero/<int:id_nurse>", "edit_nurse_profile", user.edit_nurse_profile, methods=["GET", "POST"])
    app.add_url_rule("/eliminar-enfermero/<int:id_nurse>", "delete_nurse", user.delete_nurse)
    app.add_url_rule("/enviar-recordatorio-turno", "remember_turns", user.remember_turns)

    # Ruta para el Home (usando decorator)
    @app.route("/")
    def home():
        return render_template("home.html")

    # Handlers
    app.register_error_handler(404, handler.not_found_error)
    app.register_error_handler(401, handler.unauthorized_error)
    # Implementar lo mismo para el error 500

    # Retornar la instancia de app configurada
    return app
