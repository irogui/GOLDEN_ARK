from functools import wraps
from flask import session, redirect, flash

# 1 -> admin
# 2 -> membre
# 3 -> editor

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role_id') != 1:
            flash("Accès réservé aux administrateurs.", "alert-danger")
            return redirect('/boutique')
        return f(*args, **kwargs)
    return wrapper

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'role_id' not in session:
            flash("Connexion requise", "alert-danger")
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

def editor_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if (session.get('role_id') != 1) and (session.get('role_id') != 3):
            flash("Accès réservé aux administrateurs ou éditeurs.", "alert-danger")
            return redirect('/boutique')
        return f(*args, **kwargs)
    return wrapper