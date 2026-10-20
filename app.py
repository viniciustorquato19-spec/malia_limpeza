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

# Função auxiliar para agrupar tarefas por mês em Português
def get_grouped_tasks():
    tasks = Task.query.order_by(Task.checkin.asc()).all()
    meses = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 
             7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
    
    grouped = {}
    for task in tasks:
        # Cria o título do mês (Ex: Janeiro 26)
        month_name = meses[task.checkin.month]
        year_short = task.checkin.strftime('%y')
        key = f"{month_name} {year_short}"
        
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(task)
        
    return grouped

@app.route('/')
def index():
    role = session.get('role')
    grouped_tasks = get_grouped_tasks()
    return render_template('index.html', role=role, grouped_tasks=grouped_tasks)

@app.route('/login', methods=['POST'])
def login():
    role_requested = request.form.get('role')
    password = request.form.get('password')

    if role_requested == 'admin':
        if password == '120699':  # A sua senha
            session['role'] = 'admin'
            return redirect(url_for('index'))
        else:
            grouped_tasks = get_grouped_tasks()
            return render_template('index.html', role=None, grouped_tasks=grouped_tasks, error="Senha incorreta! Tente novamente.")
            
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

# Nova Rota para Editar
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
        
    task = Task.query.get(task_id)
    if not task:
        return redirect(url_for('index'))

    if request.method == 'POST':
        guests = request.form.get('guests')
        checkin_str = request.form.get('checkin')
        checkout_str = request.form.get('checkout')
        observation = request.form.get('observation')

        if checkin_str and checkout_str and guests:
            task.guests = int(guests)
            task.checkin = datetime.strptime(checkin_str, '%Y-%m-%d').date()
            task.checkout = datetime.strptime(checkout_str, '%Y-%m-%d').date()
            task.observation = observation
            db.session.commit()
        return redirect(url_for('index'))
        
    grouped_tasks = get_grouped_tasks()
    return render_template('index.html', role='admin', grouped_tasks=grouped_tasks, edit_task=task)


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
