from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'malia_secreto_007b' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agenda.db'
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guests = db.Column(db.Integer, nullable=False)
    checkin = db.Column(db.Date, nullable=False)
    checkout = db.Column(db.Date, nullable=False)
    observation = db.Column(db.String(200))
    completed = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    role = session.get('role')
    tasks = Task.query.order_by(Task.checkin.asc()).all()
    return render_template('index.html', role=role, tasks=tasks)

@app.route('/login', methods=['POST'])
def login():
    role_requested = request.form.get('role')
    password = request.form.get('password')

    if role_requested == 'admin':
        if password == 'malia':  # Altere aqui se a sua senha for diferente
            session['role'] = 'admin'
            return redirect(url_for('index'))
        else:
            tasks = Task.query.order_by(Task.checkin.asc()).all()
            return render_template('index.html', role=None, tasks=tasks, error="Senha incorreta! Tente novamente.")
            
    elif role_requested == 'equipe':
        session['role'] = 'equipe'
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('role', None)
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add_task():
    if session.get('role') == 'admin':
        guests = request.form.get('guests')
        checkin_str = request.form.get('checkin')
        checkout_str = request.form.get('checkout')
        observation = request.form.get('observation')

        if checkin_str and checkout_str and guests:
            checkin_date = datetime.strptime(checkin_str, '%Y-%m-%d').date()
            checkout_date = datetime.strptime(checkout_str, '%Y-%m-%d').date()
            
            new_task = Task(guests=int(guests), checkin=checkin_date, checkout=checkout_date, observation=observation)
            db.session.add(new_task)
            db.session.commit()
            
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    if session.get('role') == 'equipe':
        task = Task.query.get(task_id)
        if task:
            task.completed = not task.completed
            db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if session.get('role') == 'admin':
        task = Task.query.get(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
