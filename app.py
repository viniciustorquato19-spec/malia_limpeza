from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# Chave secreta necessária para usar "sessions" (login)
app.secret_key = 'malia_secreto_007b' 
# Configura o banco de dados SQLite local
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agenda.db'
db = SQLAlchemy(app)

# --- MODELO DO BANCO DE DADOS ---
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_str = db.Column(db.String(100), nullable=False)
    task_type = db.Column(db.String(100), nullable=False)
    guest = db.Column(db.String(100))
    completed = db.Column(db.Boolean, default=False)

# Cria o banco de dados se não existir
with app.app_context():
    db.create_all()

# --- ROTAS DA APLICAÇÃO ---

@app.route('/')
def index():
    # Verifica qual é o perfil logado atual (admin ou equipe)
    role = session.get('role')
    # Puxa todas as tarefas do banco de dados (da mais recente para a mais antiga)
    tasks = Task.query.order_by(Task.id.desc()).all()
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

@app.route('/add', methods=['POST'])
def add_task():
    if session.get('role') == 'admin':
        raw_date = request.form.get('date')
        task_type = request.form.get('task_type')
        guest = request.form.get('guest')

        # Formata a data que vem do formulário HTML
        if raw_date:
            date_obj = datetime.strptime(raw_date, '%Y-%m-%dT%H:%M')
            formatted_date = date_obj.strftime('%d/%m/%Y - %H:%M')
            
            new_task = Task(date_str=formatted_date, task_type=task_type, guest=guest)
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
