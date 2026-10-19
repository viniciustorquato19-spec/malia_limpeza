from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# Chave secreta necessária para usar "sessions" (login)
app.secret_key = 'malia_secreto_007b' 
# Configura o banco de dados SQLite local
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agenda.db'
db = SQLAlchemy(app)

# --- NOVO MODELO DO BANCO DE DADOS ---
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guests = db.Column(db.Integer, nullable=False)
    checkin = db.Column(db.Date, nullable=False)
    checkout = db.Column(db.Date, nullable=False)
    observation = db.Column(db.String(200))
    completed = db.Column(db.Boolean, default=False)

# Cria o banco de dados se não existir
with app.app_context():
    db.create_all()

# --- ROTAS DA APLICAÇÃO ---
@app.route('/')
def index():
    role = session.get('role')
    # Ordena as tarefas pela data de check-in (crescente)
    tasks = Task.query.order_by(Task.checkin.asc()).all()
    return render_template('index.html', role=role, tasks=tasks)

@app.route('/login', methods=['POST'])
def login():
    role_requested = request.form.get('role')
    password = request.form.get('password')

    if role_requested == 'admin' and password == '120699':
        session['role'] = 'admin'
    elif role_requested == 'equipe':
        session['role'] = 'equipe'
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('role', None)
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    role_requested = request.form.get('role')
    password = request.form.get('password')

    if role_requested == 'admin':
        if password == 'malia':  # Altere aqui caso sua senha seja diferente
            session['role'] = 'admin'
            return redirect(url_for('index'))
        else:
            # Se a senha estiver errada, envia uma mensagem de erro
            return render_template('index.html', error="Senha incorreta! Tente novamente.")
            
    elif role_requested == 'equipe':
        session['role'] = 'equipe'
        return redirect(url_for('index'))
    
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
