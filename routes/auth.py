from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.security import check_password_hash
from modulos.tables import check_user
from functools import wraps

auth_bp = Blueprint('auth', __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or not session['role'] in ['Admin', 'Master']:
            flash('Acesso negado: você precisa ser um administrador.', 'error')
            return redirect(url_for('home.home', is_admin=True if session.get('role') == 'Admin' else False))
        return f(*args, **kwargs)
    return decorated_function


def master_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'Master':
            flash('Acesso negado: você precisa ser Master.', 'error')
            return redirect(url_for('home.home', is_admin=True if session.get('role') == 'Admin' else False))
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash('Você precisa realizar o login.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        user = check_user(username)

        if not user:
            flash('Usuário não encontrado!', 'error')
            return redirect(url_for('auth.login'))

        # Usuários que precisam de senha
        if user['role'] in ['Master', 'Admin', 'Cliente']:
            if not password or not check_password_hash(user['senha'], password):
                flash('Senha incorreta!', 'error')
                return redirect(url_for('auth.login'))

        # Clientes não precisam de senha
        session['user_id'] = user['id']
        session['username'] = user['nome']
        session['role'] = user['role']

        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('home.home'))

    return render_template('login.html')


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    return render_template('home.html')