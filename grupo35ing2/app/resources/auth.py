from app.db import db
from app.models.user import User
from flask import redirect, render_template, request, url_for, session, abort
from datetime import datetime
from dateutil.relativedelta import relativedelta

def login():

    if request.method == "GET":
        return render_template("auth/login.html")
    else:
        params = request.form

        dni = params.get("dni", "") 
        password = params.get("password", "")
        token = params.get("token", "")

        user = User.find_user_by_dni_and_password(dni=dni, password=password)

        errors = []

        if user:
            fecha_dt = datetime.strptime(user.day_of_birth, '%d/%m/%Y')
            age = relativedelta(datetime.now(), fecha_dt).years

            if user.user_role in ["admin", "nurse"]:

                session["user_dni"] = user.dni
                session["user_id"] = user.user_id
                session["user_role"] = user.user_role
                session["user_first_name"] = user.first_name
                session["covid"] = user.covid
                session["flu"] = user.flu
                session["yellow_fever"] = user.yellow_fever
                session["age"] = age
                session["risk_factor"] = user.risk_factor

            
            else:

                if token == user.token:

                    session["user_dni"] = user.dni
                    session["user_id"] = user.user_id
                    session["user_role"] = user.user_role
                    session["user_first_name"] = user.first_name
                    session["covid"] = user.covid
                    session["flu"] = user.flu
                    session["yellow_fever"] = user.yellow_fever
                    session["age"] = age
                    session["risk_factor"] = user.risk_factor

                    print(session)
            
                else:

                    errors.append("El token ingresado es incorrecto")
            
        else:

            errors.append("El dni o contraseña son incorrectos")

        if errors:
            return render_template("auth/login.html", errors=errors)
        else:
            print(session.get("user_role"))
            if session.get("user_role") == "common":
                return redirect(url_for("common_user", success="normal"))
            else:
                return redirect(url_for("home"))

def logout():
    del session["user_id"]
    del session["user_dni"]
    del session["user_role"]
    del session["user_first_name"]
    del session["covid"]
    del session["flu"]
    del session["yellow_fever"]
    del session["age"]
    del session["risk_factor"]
    
    session.clear()

    return redirect(url_for("login"))