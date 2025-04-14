
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecreto'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aulas.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Aula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)

class Horario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aula_id = db.Column(db.Integer, db.ForeignKey('aula.id'), nullable=False)
    inicio = db.Column(db.Time, nullable=False)
    fin = db.Column(db.Time, nullable=False)
    aula = db.relationship('Aula', backref=db.backref('horarios', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['nombre']
        password = request.form['password']
        user = User.query.filter_by(nombre=nombre).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Credenciales incorrectas', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/registrar_aula', methods=['GET', 'POST'])
@login_required
def registrar_aula():
    if request.method == 'POST':
        nombre = request.form['nombre']
        aula = Aula(nombre=nombre)
        db.session.add(aula)
        db.session.commit()
        flash('Aula registrada con éxito', 'success')
        return redirect(url_for('index'))
    return render_template('registrar_aula.html')

@app.route('/registrar_horario', methods=['GET', 'POST'])
@login_required
def registrar_horario():
    aulas = Aula.query.all()
    if request.method == 'POST':
        aula_id = request.form['aula_id']
        inicio = request.form['inicio']
        fin = request.form['fin']
        horario = Horario(aula_id=aula_id, inicio=inicio, fin=fin)
        db.session.add(horario)
        db.session.commit()
        flash('Horario registrado con éxito', 'success')
        return redirect(url_for('index'))
    return render_template('registrar_horario.html', aulas=aulas)

@app.route('/consultar_disponibilidad', methods=['GET', 'POST'])
@login_required
def consultar_disponibilidad():
    disponibilidad = []
    if request.method == 'POST':
        hora = request.form['hora']
        for aula in Aula.query.all():
            horarios = Horario.query.filter_by(aula_id=aula.id).all()
            libre = all(hora < h.inicio or hora >= h.fin for h in horarios)
            disponibilidad.append((aula.nombre, libre))
    return render_template('consultar_disponibilidad.html', disponibilidad=disponibilidad)

@app.route('/')
@login_required
def index():
    aulas = Aula.query.all()
    return render_template('index.html', aulas=aulas)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
