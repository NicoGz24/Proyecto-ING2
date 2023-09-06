from click import confirm
from app.db import db
from app.models.turn import Turn
from app.models.user import User
from datetime import datetime, timedelta
import random
import pdfkit
from app.utils.email import send_email
from flask import redirect, render_template, request, url_for, session, abort, make_response


def add_turn():

    turn_for_date = (datetime.now() + timedelta(days=7)).strftime("%d/%m/%Y")
    today = datetime.now().strftime("%d/%m/%Y")

    params = request.form

    user_id = session.get("user_id")

    user = User.find_user_by_id(id=user_id)

    vaccine = params.get("vaccine", "")

    sedes = ["Cementerio", "Municipal", "Terminal de Omnibus"]

    random_sede = random.choice(sedes)

    pending_turns = Turn.get_all_pending_turns_by_user_id(user_id=user_id)

    completed_turns = Turn.get_all_completed_turns_by_user_id(user_id=user_id)

    pending_for_confirmation_turns = Turn.get_all_pendig_for_confirmation_by_user_id(user_id=user_id)
    

    vaccines = Turn.get_all_vaccines_of_user_by_user_id(user_id=user_id)

    covid_amount = Turn.get_amount_of_pending_covid_turn_by_user_id(user_id=user_id)

    errors = []

    vaccines_covid = 0

    for v in vaccines:
        if "Covid 19" in v:
            vaccines_covid += 1

    if user.covid == 1 and vaccines_covid == 2 and vaccine =="Covid 19":
        errors.append(f"Usted ya cuenta con un turno pendiente o completado de la vacuna: {vaccine}")
    elif covid_amount == 1 and vaccine =="Covid 19":
        errors.append(f"Usted ya cuenta con un turno pendiente o completado de la vacuna: {vaccine}")
    elif vaccine in ["Fiebre Amarilla", "Gripe"]:
        if vaccine in vaccines:
            errors.append(f"Usted ya cuenta con un turno pendiente o completado de la vacuna: {vaccine}")
    
    if errors:
        return render_template("user/common_user.html", pending_turns=pending_turns, completed_turns=completed_turns, pending_for_confirmation_turns=pending_for_confirmation_turns, errors=errors)
    else:

        if vaccine == "Covid 19":

            if session.get("covid") == 1:
                vaccine = f"Segunda Dosis {vaccine}"
            else:
                vaccine = f"Primera Dosis {vaccine}"
        
        if vaccine == "Fiebre Amarilla":
            turn = Turn(
                status="pendiente por confirmacion",
                created_at=today,
                completed_at=turn_for_date,
                vaccine=vaccine,
                sede=random_sede,
                user_id=user_id
            )
            turn.add_turn()
            subject = f"Turno Solicitado Exitosamente {session.get('user_first_name')}"
            message = f"""
                Recuerde que el turno esta sujeto a aceptacion por el administrador
                \n
                Turno Numero: {turn.turn_id}
                \n
                Vacuna: {turn.vaccine}
                \n
                Sede: {turn.sede}
                \n
                Fecha de Solicitud: {turn.created_at}
                \n
                Fecha de Aplicacion: {turn.completed_at}
                \n
                Estado: {turn.status}
            """
        else:
            turn = Turn(
                status="pendiente",
                created_at=today,
                completed_at=turn_for_date,
                vaccine=vaccine,
                sede=random_sede,
                user_id=user_id
            )
            turn.add_turn()
            subject = f"Turno Solicitado Exitosamente {session.get('user_first_name')}"
            message = f"""
                Turno Numero: {turn.turn_id}
                \n
                Vacuna: {turn.vaccine}
                \n
                Sede: {turn.sede}
                \n
                Fecha de Solicitud: {turn.created_at}
                \n
                Fecha de Aplicacion: {turn.completed_at}
                \n
                Estado: {turn.status}
            """
        
        user = User.find_user_by_id(id=user_id)
        user_email = user.email
        
        send_email(subject=subject, to=user_email, message=message)

        return redirect(url_for("common_user", success="turno-registrado-exitosamente"))


def cancel_turn(turn_id: int):

    turn_to_cancel = Turn.get_turn_by_id(turn_id=turn_id)

    turn_to_cancel.cancel_turn()

    return redirect(url_for("common_user", success="normal"))


def nurse_cancel_turn(turn_id: int):

    turn_to_cancel = Turn.get_turn_by_id(turn_id=turn_id)

    turn_to_cancel.cancel_turn()

    return redirect(url_for("nurse_user", success="normal"))
    
def confirm_turn(turn_id):
    turn = Turn.get_turn_by_id(turn_id)
    nurse_id = session.get("user_id")
    patient = User.find_user_by_id(id=turn.user_id)
    nurse = User.find_user_by_id(id=nurse_id)

    if not turn.laboratory:
        turn.laboratory = " "
    if not turn.lot:
        turn.lot = " "
    if not turn.observations:
        turn.observations=""

    if request.method == "GET":
        return render_template("user/confirm_turn.html", nurse=nurse, patient=patient, turn=turn)
    else:
        data = request.form
        laboratory = data.get("laboratory", "")
        lot = data.get("lot", "")
        observations = data.get("observations", "")


        Turn.confirm_turn(turn,laboratory,lot,observations) 
        User.update_vaccine(turn.user_id, turn.vaccine)

        pending_turns = Turn.get_all_pending_turns_by_sede_of_the_day(turn.sede)

        if "Covid 19" in turn.vaccine and patient.covid == 1:
            send_second_turn_covid19(turn.user_id, "Segunda Dosis Covid 19")
        return render_template("user/nurse_user.html", nurse=nurse, patient=patient, pending_turns=pending_turns,success_register="Turno confirmado exitosamente")
 



def download_certificate_turn(turn_id: int):

    completed_turn = Turn.get_turn_by_id(turn_id=turn_id)
    user = User.find_user_by_id(id=completed_turn.user_id)

    rendered = render_template("certificate_template.html", completed_turn=completed_turn, user=user)

    pdf = pdfkit.from_string(rendered, False)

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=certificado.pdf"

    return response




def send_second_turn_covid19(user_id:int, vaccine:str):

    turn_for_date = (datetime.now() + timedelta(days=7)).strftime("%d/%m/%Y")
    today = datetime.now().strftime("%d/%m/%Y")

    sedes = ["Cementerio", "Municipal", "Terminal de Omnibus"]

    random_sede = random.choice(sedes)
    
    turn = Turn(
        status="pendiente",
        created_at=today,
        completed_at=turn_for_date,
        vaccine=vaccine,
        sede=random_sede,
        user_id=user_id
    )
    turn.add_turn()
    user = User.find_user_by_id(id=user_id)
    user_email = user.email
    subject = f"Turno Automatico Covid19 - Segunda dosis {user.first_name}"
    message = f"""
        Estimado usuario, este mail es automatico no debe responderlo.
        \n
        \n
        Turno Numero: {turn.turn_id}
        \n
        Vacuna: {turn.vaccine} 
        \n
        Sede: {turn.sede}
        \n
        Fecha de Solicitud: {turn.created_at}
        \n
        Fecha de Aplicacion: {turn.completed_at}
        \n
        Estado: {turn.status}
        """
    
    send_email(subject=subject, to=user_email, message=message)


def patient_details(patient_id: int):

    patient = User.find_user_by_id(id=patient_id)

    completed_turns = Turn.get_all_completed_turns_by_user_id(user_id=patient_id)

    return render_template("user/patient_details.html", patient=patient, completed_turns=completed_turns)

def admin_reports():
    
    if request.method == "GET":
        vaccines_count = {
                "Covid 19": 0,
                "Fiebre Amarilla": 0,
                "Gripe": 0
            }
        return render_template(
            "user/admin_reports.html", 
            ok=False,
            from_date="",
            to_date="",
            sede="",
            vaccine="",
            status="",
            vaccines_count=vaccines_count,
            turns_filtered=[],
            total_vaccines=0
            )
    else:
        params = request.form
        from_date = datetime.strptime(params.get("from_date"), '%Y-%m-%d').date()
        to_date = datetime.strptime(params.get("to_date"), '%Y-%m-%d').date()
        status = params.get("status")
        sede = params.get("sede")
        vaccine = params.get("vaccine")

        errors = []

        if from_date > to_date:
            errors.append("La fecha desde no puede ser mayor que la fecha hasta")
        
        if errors:
            vaccines_count = {
                "Covid 19": 0,
                "Fiebre Amarilla": 0,
                "Gripe": 0
            }
            return render_template("user/admin_reports.html", errors=errors, vaccines_count=vaccines_count) 
        else:

            turns_filtered = Turn.get_turns_between_two_dates(
                from_date=from_date,
                to_date=to_date,
                status=status,
                sede=sede,
                vaccine=vaccine
            )

            vaccines_count = {
                "Covid 19": 0,
                "Fiebre Amarilla": 0,
                "Gripe": 0
            }

            for turn_filtered in turns_filtered:
                if "Covid 19" in turn_filtered.vaccine:
                    vaccines_count["Covid 19"] += 1
                elif "Fiebre Amarilla" in turn_filtered.vaccine:
                    vaccines_count["Fiebre Amarilla"] += 1
                elif "Gripe" in turn_filtered.vaccine:
                    vaccines_count["Gripe"] += 1


            total_vaccines = vaccines_count["Covid 19"] + vaccines_count["Fiebre Amarilla"] + vaccines_count["Gripe"]

            return render_template(
                "user/admin_reports.html", 
                turns_filtered=turns_filtered, 
                ok=True,
                from_date=from_date,
                to_date=to_date,
                sede=sede,
                vaccine=vaccine,
                status=status,
                vaccines_count=vaccines_count,
                total_vaccines=total_vaccines
                )


def admin_yellow_fever_turns():

    pending_turns = Turn.get_all_pending_for_confirmated_yellow_fever_turns()

    return render_template(
        "user/admin_yellow_fever_turns.html",
        pending_turns=pending_turns
        )

def admin_cancel_turn(turn_id: int):

    turn_to_cancel = Turn.get_turn_by_id(turn_id=turn_id)

    turn_to_cancel.cancel_turn()

    return redirect(url_for("admin_yellow_fever_turns"))

def admin_confirm_turn(turn_id: int):
    

    turn_to_confirm = Turn.get_turn_by_id(turn_id=turn_id)

    turn_to_confirm.admin_confirm_turn()
    pending_turns = Turn.get_all_pending_for_confirmated_yellow_fever_turns()

    user = User.find_user_by_id(id=turn_to_confirm.user_id)
    user_email = user.email
    subject = f"Su turno para la Fiebre Amarilla ha sido confirmado exitosamente {user.first_name}"
    message = f"""
        Estimado usuario, este mail es automatico no debe responderlo.
        \n
        \n
        Su turno para la Fiebre Amarilla ha sido confirmado por el administrador 
        \n
        \n
        Turno Numero: {turn_to_confirm.turn_id}
        \n
        Vacuna: {turn_to_confirm.vaccine} 
        \n
        Sede: {turn_to_confirm.sede}
        \n
        Fecha de Solicitud: {turn_to_confirm.created_at}
        \n
        Fecha de Aplicacion: {turn_to_confirm.completed_at}
        \n
        Estado: {turn_to_confirm.status}
        """
    
    send_email(subject=subject, to=user_email, message=message)


    return render_template(
        "user/admin_yellow_fever_turns.html",
        pending_turns=pending_turns,
        success_register="Turno confirmado exitosamente"
        )