from email.mime import message
from app.db import db
from app.models.user import User
from app.models.turn import Turn
from flask import redirect, render_template, request, url_for, session, abort
from datetime import datetime
from dateutil.relativedelta import relativedelta
from app.utils.email import send_email


def user_register():
    
    if request.method == "GET":
        return render_template("user/user_register.html")
    else:
        params = request.form

        first_name = params.get("first_name", "")
        last_name = params.get("last_name", "")
        email = params.get("email", "")
        dni = params.get("dni", "")
        day_of_birth = params.get("day_of_birth", "")
        password = params.get("password", "")
        confirm_password = params.get("confirm_password", "")
        covid_first = 1 if params.get("covid_first", "off") == "on" else 0
        covid_second = 1 if params.get("covid_second", "off") == "on" else 0
        yellow_fever =1 if params.get("yellow_fever", "off") == "on" else 0
        flu = 1 if params.get("flu", "off") == "on" else 0
        risk_factor = 1 if params.get("risk_factor", "off") == "on" else 0

        covid = covid_first + covid_second 

        errors = []
        if password != confirm_password:
            errors.append("La contraseña ingresada no coincide con el confirmar contraseña")
        
        if covid_first == 0 and covid_second == 1:
            errors.append("No se puede marcar la segunda dosis de covid sin haber aplicado la primera")
        
        if len(day_of_birth) != 10:
            errors.append("El formato de la fecha de nacimiento es incorrecto")
        elif day_of_birth[2] != "/" and day_of_birth[5] != "/":
            errors.append("El formato de la fecha de nacimiento es incorrecto")

        if not dni.isnumeric():
            errors.append("El formato del dni es invalido")
        else:
            errors.extend(User.exist_dni_or_email(dni=dni, email=email))

        if not errors: ## Si no hay ningun error entonces crea el usuario en la base con rol de usuario comun
            new_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                dni=dni,
                password=password,
                day_of_birth=day_of_birth,
                user_role="common",
                covid=covid,
                yellow_fever=yellow_fever,
                flu=flu,
                token="1234",
                risk_factor=risk_factor
            )
            new_user.add_user()
            return render_template("user/user_register.html", success_register="Registro exitoso se generó un Token: 1234 automáticamente recuerde guardarlo ya que lo necesitará  para iniciar sesión")
        else:
            return render_template("user/user_register.html", errors=errors)

def user_profile():
    user = User.find_user_by_id(session['user_id'])
    fecha_dt = datetime.strptime(user.day_of_birth, '%d/%m/%Y')
    edad = relativedelta(datetime.now(), fecha_dt)
    return render_template("user/user_profile.html",user=user, edad=edad)

def edit_user_profile():
    user = User.find_user_by_id(session['user_id'])
    fecha_dt = datetime.strptime(user.day_of_birth, '%d/%m/%Y')
    edad = relativedelta(datetime.now(), fecha_dt)
    if request.method == "GET":
        return render_template("user/edit_user_profile.html", user=user,edad=edad)
    else:
        data = request.form
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        dni = data.get("dni", "")
        email = data.get("email", "")
        day_of_birth = data.get("day_of_birth", "")
        errors = []
        if user.email != email: 
            errors.extend(User.exist_email(email=email))
        if len(day_of_birth) != 10:
            errors.append("El formato de la fecha de nacimiento es incorrecto")
        elif day_of_birth[2] != "/" and day_of_birth[5] != "/":
            errors.append("El formato de la fecha de nacimiento es incorrecto")
        if not dni.isnumeric():
            errors.append("El formato del dni es invalido")
        elif user.dni != dni:
            errors.extend(User.exist_dni_or_email(dni=dni, email="^%^&&_)(@tryip.com"))
        if not errors:
            User.update_profile(user.user_id,email,dni,first_name,last_name,day_of_birth)
            session["user_first_name"] = user.first_name
            return render_template("user/edit_user_profile.html", user=user,edad=edad , success_edit_profile="Los cambios han sido guardado con exito")
        else:
            return render_template("user/edit_user_profile.html", user=user,edad=edad , errors=errors)


def common_user(success: str = ""):
    user_id = session.get("user_id")

    pending_turns = Turn.get_all_pending_turns_by_user_id(user_id=user_id)

    completed_turns = Turn.get_all_completed_turns_by_user_id(user_id=user_id)

    pending_for_confirmation_turns = Turn.get_all_pendig_for_confirmation_by_user_id(user_id=user_id)

    if success == "turno-registrado-exitosamente":
        return render_template("user/common_user.html", pending_turns=pending_turns, completed_turns=completed_turns, pending_for_confirmation_turns=pending_for_confirmation_turns, success_register="Turno registrado exitosamente")
    else:
        return render_template("user/common_user.html", pending_turns=pending_turns, completed_turns=completed_turns, pending_for_confirmation_turns=pending_for_confirmation_turns)


def nurses_management():
    nurses = User.get_all_nurses_list() 
    turns_pending=Turn.get_all_pending_turns_of_the_day()
    cant_turns= turns_pending.__len__()
    return render_template("user/nurses_management.html",cant_turns=cant_turns ,nurses=nurses)

def nurse_register():

    nurses = User.get_all_nurses_list() 

    params = request.form

    first_name = params.get("first_name", "")
    last_name = params.get("last_name", "")
    email = params.get("email", "")
    dni = params.get("dni", "")
    day_of_birth = params.get("day_of_birth", "")
    password = params.get("password", "")
    user_sede = params.get("user_sede", "")


    errors = []
    if len(day_of_birth) != 10:
        errors.append("El formato de la fecha de nacimiento es incorrecto")
    elif day_of_birth[2] != "/" and day_of_birth[5] != "/":
        errors.append("El formato de la fecha de nacimiento es incorrecto")

    if not dni.isnumeric():
        errors.append("El formato del dni es invalido")
    else:
        errors.extend(User.exist_dni_or_email(dni=dni, email=email))
    
    if not errors:
        new_nurse = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            password=password,
            day_of_birth=day_of_birth,
            user_role="nurse",
            user_sede=user_sede
        )
        new_nurse.add_user()

        subject = f"{new_nurse.first_name} fuiste registrado como enfermero en VACUNASSIST"
        message = f"""
            Hola {new_nurse.first_name} fuiste registrado como enfermero en VACUNaSSIST \n
            Necesitaras las siguientes credenciales para poder iniciar sesion DNI y contraseña \n
            DNI = {new_nurse.dni} \n
            Contraseña = {new_nurse.password} \n
            Recuerda que no necesitaras del token para poder ingresar
        """
        
        send_email(subject=subject, to=new_nurse.email, message=message)
        return redirect(url_for('nurses_management'))
    else:
        turns_pending=Turn.get_all_pending_turns_of_the_day()
        cant_turns= turns_pending.__len__()
        return render_template("user/nurses_management.html", cant_turns=cant_turns,errors=errors, nurses=nurses)

def nurse_user():
    user_id = session.get("user_id")
    nurse = User.find_user_by_id(user_id)
    sede = nurse.user_sede

    pending_turns = Turn.get_all_pending_turns_by_sede_of_the_day(sede=sede)      

    return render_template("user/nurse_user.html", nurse=nurse, pending_turns=pending_turns)

def edit_nurse_profile(id_nurse):
    nurse = User.find_user_by_id(id_nurse)
    fecha_dt = datetime.strptime(nurse.day_of_birth, '%d/%m/%Y')
    edad = relativedelta(datetime.now(), fecha_dt)
    if request.method == "GET":
        return render_template("user/edit_nurse_profile.html", nurse=nurse,edad=edad)
    else:
        data = request.form
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        dni = data.get("dni", "")
        email = data.get("email", "")
        day_of_birth = data.get("day_of_birth", "")
        user_sede = data.get("user_sede","")
        password = data.get("password","")
        errors = []
        if nurse.email != email: 
            errors.extend(User.exist_email(email=email))
        if len(day_of_birth) != 10:
            errors.append("El formato de la fecha de nacimiento es incorrecto")
        elif day_of_birth[2] != "/" and day_of_birth[5] != "/":
            errors.append("El formato de la fecha de nacimiento es incorrecto")
        if not dni.isnumeric():
            errors.append("El formato del dni es invalido")
        elif nurse.dni != dni:
            errors.extend(User.exist_dni_or_email(dni=dni, email="^%^&&_)(@tryip.com"))
        if not errors:
            User.update_nurse_profile(nurse.user_id,email,dni,first_name,last_name,day_of_birth,user_sede,password)
            return render_template("user/edit_nurse_profile.html", nurse=nurse,edad=edad, success_edit_nurse_profile="Los cambios han sido guardado con exito")
        else:
            return render_template("user/edit_nurse_profile.html", nurse=nurse,edad=edad, errors=errors)

def nurse_profile(id_nurse):
    nurse = User.find_user_by_id(id_nurse)
    fecha_dt = datetime.strptime(nurse.day_of_birth, '%d/%m/%Y')
    edad = relativedelta(datetime.now(), fecha_dt)
    return render_template("user/nurse_profile.html",nurse=nurse, edad=edad)

def delete_nurse(id_nurse):
    User.delete_nurse(id_nurse)
    nurses = User.get_all_nurses_list()
    turns_pending=Turn.get_all_pending_turns_of_the_day()
    cant_turns= turns_pending.__len__()
    return render_template("user/nurses_management.html",cant_turns=cant_turns,nurses=nurses)

def remember_turns():
    turns_pending=Turn.get_all_pending_turns_of_the_day()
    cant_turns= turns_pending.__len__()
    print("cantidad de turnos:", cant_turns)
    for turn in turns_pending:
        user = User.find_user_by_id(turn.user_id)
        subject = f"Recordatorio Vacunassist de turno pendiente"
        message = f"""
            Estimado usuario, este mail es automatico no debe responderlo.
            \n
            Desde Vacunassist queremos recordarle que el dia  {turn.completed_at} debera presentarse
            en la sede {turn.sede} para la aplicacion de la vacuna {turn.vaccine}. Recuerde que su
            numero de turno es el {turn.turn_id}
            """
        send_email(subject=subject, to=user.email, message=message)
    nurses = User.get_all_nurses_list()
    return render_template("user/nurses_management.html",cant_turns=cant_turns,nurses=nurses,success_remember_turns='Se han enviado los recordatorios con exito')