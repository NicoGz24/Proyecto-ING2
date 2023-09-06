from unittest import load_tests
from sqlalchemy import true
from app.db import db
from datetime import date
from datetime import datetime
# from app.models.user import User


class Turn(db.Model):
    __tablename__ = "turnos"
    turn_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(45), unique=False, nullable=False)
    created_at = db.Column(db.String(45), unique=False, nullable=False)
    completed_at = db.Column(db.String(45), unique=False, nullable=True)
    vaccine = db.Column(db.String(45), unique=False, nullable=False)
    sede = db.Column(db.String(45), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.user_id')) 
    laboratory = db.Column(db.String(45), unique=False, nullable=true)
    lot = db.Column(db.String(45), unique=False, nullable=true)
    observations = db.Column(db.String(45), unique=False, nullable=true)
    created_at_date = db.Column(db.Date, default=datetime.now().date())
    

    def __init__(self, status: str, created_at: str, vaccine: str, sede: str, user_id: int, completed_at: str = None, laboratory: str = None , lot: str = None, observations: str = None ) -> None:
        self.status = status
        self.created_at = created_at
        self.vaccine = vaccine
        self.sede = sede
        self.user_id = user_id
        self.completed_at = completed_at
        self.laboratory = laboratory
        self.lot = lot
        self.observations = observations
    
    def add_turn(self):
        db.session.add(self)
        db.session.commit()
    
    def cancel_turn(self):
        self.status="cancelado"
        db.session.commit()

    def confirm_turn(self,laboratory,lot,observations):

        if not observations:
            observations=None
        self.laboratory = laboratory
        self.lot = lot
        self.observations = observations
        self.status="completado"
        db.session.commit()

    def get_turn_by_id(turn_id: int) -> object:

        turn = Turn.query.filter(Turn.turn_id == turn_id).first()
        return turn
    
    def get_all_vaccines_of_user_by_user_id(user_id: int) -> list:

        # all_turns = Turn.query.filter((Turn.user_id == user_id) & (Turn.status == "pendiente") | (Turn.user_id == user_id) & (Turn.status == "completado")).all()
        all_turns = Turn.query.filter((Turn.user_id == user_id) & ((Turn.status == "pendiente") | (Turn.status == "completado") | (Turn.status == "pendiente por confirmacion"))).all()
        vaccines = [turn.vaccine for turn in all_turns]

        return vaccines

    def get_all_pending_turns_by_user_id(user_id: int) -> list:

        pending_turns = Turn.query.filter((Turn.user_id == user_id) & (Turn.status == "pendiente")).all()

        return pending_turns
    
    def get_all_completed_turns_by_user_id(user_id: int) -> list:

        completed_turns = Turn.query.filter((Turn.user_id == user_id) & (Turn.status == "completado")).all() 

        return completed_turns
    
    def get_all_pendig_for_confirmation_by_user_id(user_id: int) -> list:

        pending_for_confirmation_turns = Turn.query.filter((Turn.user_id == user_id) & (Turn.status == "pendiente por confirmacion")).all() 

        return pending_for_confirmation_turns

    def get_all_pending_turns_by_sede_of_the_day (sede: str) -> list:
        #cambiar el condicional de Turn.created_at  Turn.completed_at     datetime.now()
        fecha = date.today().strftime('%d/%m/%Y')
        pending_turns = Turn.query.filter((Turn.sede == sede) & (Turn.status == "pendiente") & (Turn.completed_at == fecha )).all()

        return pending_turns
    
    def get_amount_of_pending_covid_turn_by_user_id(user_id: int):

        all_turns = Turn.query.filter((Turn.user_id == user_id) & (Turn.status == "pendiente") & (Turn.vaccine.like(f"%Covid 19%"))).all() #Turn.vaccine == "Covid 19"
        covid_amount = len(all_turns)
        return covid_amount

    def get_turns_between_two_dates(from_date: str, to_date: str, status: str, sede: str, vaccine: str) -> list:
        
        if status == "No aplicar" and sede == "No aplicar" and vaccine == "No aplicar":
            turns_filtered = Turn.query.filter(Turn.created_at_date.between(from_date, to_date)).all()
        elif sede == "No aplicar" and vaccine == "No aplicar":
            turns_filtered = Turn.query.filter(Turn.created_at_date.between(from_date, to_date) & (Turn.status == status)).all()
        elif status == "No aplicar" and vaccine == "No aplicar":
            turns_filtered = Turn.query.filter(Turn.created_at_date.between(from_date, to_date) & (Turn.sede == sede)).all()
        elif status == "No aplicar" and sede == "No aplicar":
            turns_filtered = Turn.query.filter(Turn.created_at_date.between(from_date, to_date) & (Turn.vaccine.like(f"%{vaccine}%"))).all()
        elif vaccine == "No aplicar":
            turns_filtered = Turn.query.filter(Turn.created_at_date.between(from_date, to_date) & (Turn.status == status) & (Turn.sede == sede)).all()
        elif sede == "No aplicar":
            turns_filtered = Turn.query.filter(Turn.created_at_date.between(from_date, to_date) & (Turn.status == status) & (Turn.vaccine.like(f"%{vaccine}%"))).all()
        elif status == "No aplicar":
            turns_filtered = Turn.query.filter(Turn.created_at_date.between(from_date, to_date) & (Turn.sede == sede) & (Turn.vaccine.like(f"%{vaccine}%"))).all()
        else:
            turns_filtered = Turn.query.filter(Turn.created_at_date.between(from_date, to_date) & (Turn.status == status) & (Turn.sede == sede) & (Turn.vaccine.like(f"%{vaccine}%"))).all()

        return turns_filtered

    def get_all_pending_for_confirmated_yellow_fever_turns():
        pending_turns = Turn.query.filter((Turn.status == "pendiente por confirmacion")).all()
        return pending_turns

    def admin_confirm_turn(self):
        self.status="pendiente"
        db.session.commit()
        
    def get_all_pending_turns_of_the_day () -> list:
        fecha = date.today().strftime('%d/%m/%Y')
        pending_turns = Turn.query.filter((Turn.status == "pendiente") & (Turn.completed_at == fecha )).all()
        print("  ")
        print("----ADENTRO DEL PENDING-----")
        print("  ")
        return pending_turns
