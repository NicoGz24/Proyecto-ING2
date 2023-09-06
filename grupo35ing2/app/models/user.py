# from sqlalchemy.orm import backref
from app.db import db
# from werkzeug.security import generate_password_hash, check_password_hash
from app.models.turn import Turn

class User(db.Model):
    
    __tablename__ = "usuarios"
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(45), unique=True, nullable=False)
    first_name= db.Column(db.String(45), unique=False, nullable=False)
    last_name = db.Column(db.String(45), unique=False, nullable=False)
    dni = db.Column(db.String(45), unique=True, nullable=False)
    password = db.Column(db.String(255), unique=False, nullable=True) 
    day_of_birth = db.Column(db.String(45), unique=False, nullable=False) # 06/09/1999
    user_role = db.Column(db.String(45), unique=False, nullable=False) #admin, common_user, nurse
    token = db.Column(db.String(45), unique=False, nullable=True)
    covid = db.Column(db.Integer, unique=False, nullable=True) # 1 una dosis 2 dos dosis 0 cero dosis
    flu = db.Column(db.Integer, unique=False, nullable=True) # 1 una dosis 0 cero dosis
    yellow_fever = db.Column(db.Integer, unique=False, nullable=True) # 1 una dosis 0 cero dosis
    risk_factor = db.Column(db.Integer, unique=False, nullable=True) 
    user_sede = db.Column(db.String(45), unique=False, nullable=True)
    turns = db.relationship(Turn, backref='user_turn')

    def __init__(self, 
    email: str, 
    first_name: str, 
    last_name: str, 
    dni: str, 
    password: str, 
    day_of_birth: str, 
    user_role: str, 
    token: str = None, 
    covid: int = None, 
    flu: int = None, 
    yellow_fever: int = None, 
    risk_factor: int = None,
    user_sede: str = None):
        self.dni = dni
        self.flu = flu
        self.email = email
        self.covid = covid
        self.token = token
        self.password = password
        self.last_name = last_name
        self.user_role = user_role
        self.first_name = first_name
        self.risk_factor = risk_factor
        self.yellow_fever = yellow_fever
        self.day_of_birth = day_of_birth
        self.user_sede = user_sede
    

    def add_user(self):
        db.session.add(self)
        db.session.commit()

    def exist_dni_or_email(dni: str, email: str):
        errors=[]
        if User.query.filter(User.dni == dni).first():
            errors.append("El dni ingresado ya se encuentra registrado")
        if User.query.filter(User.email == email).first():
            errors.append("El email ya se encuentra registrado")
        return errors
    
    def find_user_by_dni_and_password(dni: str, password: password):

        user = User.query.filter(User.dni == dni).first()
        if user:
            if user.password == password:
                return user
        return None
    
    def find_user_by_id(id: int):
        user = User.query.filter(User.user_id == id).first()
        if user:
            return user
        return None
    
    def exist_email(email: str):
        errors=[]
        if User.query.filter(User.email == email).first():
            errors.append("El email ya se encuentra registrado")
        return errors

    def update_profile(id:int, email:str, dni: int, first_name: str, last_name:str,day_of_birth:str):
        user = User.query.filter(User.user_id == id).first()
        user.first_name = first_name
        user.dni = dni
        user.email = email
        user.last_name = last_name
        user.day_of_birth = day_of_birth
        db.session.add(user)
        db.session.commit()
    
    def get_all_nurses_list():
        nurses = User.query.filter(User.user_role == "nurse").all()
        return nurses

    def update_vaccine(user_id:int, vaccine:str):
        user = User.query.filter(User.user_id == user_id).first()
        if vaccine == "Gripe":
            user.flu = 1
        if vaccine == "Fiebre Amarilla":
            user.yellow_fever = 1
        if "Covid 19" in vaccine and user.covid == 0:
            user.covid = 1
        elif "Covid 19" in vaccine and user.covid == 1:
            user.covid=2  
        db.session.add(user)
        db.session.commit()  


    def update_nurse_profile(id:int, email:str, dni: int, first_name: str, last_name:str,day_of_birth:str,user_sede:str, password:str):
        user = User.query.filter(User.user_id == id).first()
        user.first_name = first_name
        user.dni = dni
        user.email = email
        user.last_name = last_name
        user.day_of_birth = day_of_birth
        user.user_sede=user_sede
        user.password=password
        db.session.add(user)
        db.session.commit()

    def delete_nurse(id:int):
        nurse = User.query.filter(User.user_id == id).first()
        db.session.delete(nurse)
        db.session.commit()