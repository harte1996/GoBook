from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from routes.auth import login_required
from werkzeug.security import check_password_hash
from functools import wraps

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
@login_required
def home():
    # Pasta do usuário logado
    username = str(session.get('username')).upper()
    return render_template('home.html', username=username, is_admin=True if session.get('role') in ['Admin','Master'] else False)