from flask import Flask, request, render_template, redirect, flash, session, g, Blueprint, url_for
from connexion_db import get_db
import requests
import secrets
import uuid
import json
import time

# Encryption mdp
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__, template_folder='templates')


@auth.route('/login', methods=['GET'])
def auth_login():
    return render_template('auth/login.html')

@auth.route('/login', methods=['POST'])
def valid_auth_login():
    identifiant = request.form['identifiant']
    mdp_membre = request.form['mdp_membre']

    # Importance notable du BINRAY de la condition de la requête pour faire attention à la casse.
    mycursor = get_db().cursor()
    sql = ''' SELECT id_membre,
                     nom_membre,
                     mdp_membre,
                     role_id       
              FROM Membre 
              WHERE BINARY nom_membre = %s; '''
    mycursor.execute(sql, identifiant)

    membre = mycursor.fetchone()

    if membre:
        if check_password_hash(membre['mdp_membre'], mdp_membre):

            session['id_membre'] = membre['id_membre']
            session['nom_membre'] = membre['nom_membre']
            session['role_id'] = membre['role_id']

            flash(f"Bienvenue {membre['nom_membre']} !", 'alert-warning')
            return redirect("/boutique")
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect", 'alert-warning')
            return redirect('/login')
    else:
        flash("Nom d'utilisateur ou mot de passe incorrect", 'alert-warning')
        return redirect('/login')


@auth.route('/logout')
def auth_logout():
    session.pop('role_id', None)
    session.pop('id_membre', None)
    session.pop('nom_membre', None)
    session.pop('gold', None)

    flash("Vous avez bien été déconnecté !", 'alert-warning')
    return redirect("/")


@auth.route('/forget-password', methods=['GET'])
def forget_password():
    return render_template('auth/forget_password.html')



# ----------------------
# Register
# ----------------------


# Étape 1


def vérification_existante(id: str) -> bool:
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) as nbr
            FROM Membre
            WHERE id_membre = %s AND role_id != 4;
        """, (id,))
        num = cur.fetchone()["nbr"]

    return num > 0


@auth.route('/register/step1', methods=['GET', 'POST'])
def register_step1():
    session['register_step'] = 1

    if "session-id" not in session:
        session["session-id"] = str(uuid.uuid4())

    if request.method == 'POST':
        # On génère le code
        session_id = session["session-id"]
        onetime_code = secrets.randbelow(1000000)
        now = int(time.time())
        expires = now + 600            # 10 minutes


        discord_id = request.form['discord-id']
        if vérification_existante(discord_id) :
            flash("Ce compte discord est déjà lié à un compte sur ce site. Veuillez en choisir un autre.", 'alert-warning')


        else :
            # ----- On enregistre le code -----
            db = get_db()
            with db.cursor() as cur:
                cur.execute("""
                    INSERT INTO Otp_sessions (session_id, otp, expires_at)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE otp = VALUES(otp), expires_at = VALUES(expires_at)
                """, (session_id, onetime_code, expires))
            db.commit()
            # ---------------------------------

            message = f"Le **code** à **usage unique** est :\n```\n{onetime_code}\n```"

            # On envoie la requête
            result = requests.post(
                "http://127.0.0.1:9814/send-dm",
                json={
                    "discordId": discord_id,
                    "message": f"{message}"
                },
                headers={"Authorization": "SECRET_KEY"}
            )


            # On agis dans le cas où la requête ne s'est pas bien passée et dans le cas où elle s'est bien passée
            if result.status_code != 200 :
                flash("Une erreur est survenue, votre identifiant est peut-être erroné.", 'alert-warning')
            else :
                session['discord-id'] = request.form['discord-id']
                session['register_step'] = 2
                return redirect(url_for('auth.register_step2'))

    return render_template('auth/register/step1.html')






# Étape 2

def _send_registration_otp(discord_id):
    """
    Permet de renvoyer un code otp via le bot IZARIX à un utilisateur en passant par son identifiant
    """
    session_id = session["session-id"]
    onetime_code = secrets.randbelow(1000000)
    now = int(time.time())
    expires = now + 600            # 10 minutes


    db = get_db()
    with db.cursor() as cur:
        cur.execute("""
            INSERT INTO Otp_sessions (session_id, otp, expires_at)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE otp = VALUES(otp), expires_at = VALUES(expires_at)
        """, (session_id, onetime_code, expires))
    db.commit()

    message = f"Le **code** à **usage unique** est :\n```\n{onetime_code}\n```"

    return requests.post(
        "http://127.0.0.1:9814/send-dm",
        json={
            "discordId": discord_id,
            "message": message
        },
        headers={"Authorization": "SECRET_KEY"}
    )


@auth.route('/register/resend-code')
def register_resend_code():
    if session.get('register_step', 1) < 2:
        return redirect(url_for('auth.register_step1'))

    if not session.get('discord-id'):
        flash("Aucun identifiant Discord enregistré. Recommencez la procédure.", 'alert-warning')
        return redirect(url_for('auth.register_step1'))

    if "session-id" not in session:
        session["session-id"] = str(uuid.uuid4())

    result = _send_registration_otp(session['discord-id'])
    if result.status_code != 200:
        flash("Impossible de renvoyer le code pour le moment. Vérifiez votre identifiant Discord.", 'alert-warning')
    else:
        flash("Un nouveau code a été envoyé sur Discord.", 'alert-warning')

    return redirect(url_for('auth.register_step2'))




def _verif_validitee_otps() :
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""
            DELETE FROM Otp_sessions
            WHERE expires_at <= UNIX_TIMESTAMP();
        """)
    db.commit()




def verify_otp(submitted) -> bool:
    if not submitted:
        return False
    session_id = session["session-id"]

    db = get_db()
    with db.cursor() as cur:
        cur.execute("""
            SELECT otp FROM Otp_sessions
            WHERE session_id = %s AND expires_at > UNIX_TIMESTAMP()
        """, (session_id,))
        row = cur.fetchone()

    return row and row['otp'] == int(submitted)




@auth.route('/register/step2', methods=['GET', 'POST'])
def register_step2():
    if session.get('register_step', 1) < 2:
        return redirect(url_for('auth.register_step1'))

    if request.method == 'POST':

        _verif_validitee_otps()

        res = verify_otp(request.form.get('otp'))
        if res :

            session_id = session["session-id"]

            db = get_db()
            with db.cursor() as cur:
                cur.execute("""
                    DELETE FROM Otp_sessions
                    WHERE session_id = %s;
                """, (session_id,))
            db.commit()

            session['register_step'] = 3
            return redirect(url_for('auth.register_step3'))
        else :
            flash("Le code à usage unique est erroné", 'alert-warning')

    return render_template('auth/register/step2.html')





# Étape 3

# def verifier_id_discord_existant(id: str) -> bool:
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute("""
#             SELECT COUNT(*) as nbr
#             FROM Membre
#             WHERE id_membre = %s;
#         """, (id,))
#         num = cur.fetchone()["nbr"]

#     return num > 0


def _verify(discord_id, identifiant):
    """
    Permet de définir un membre comme vérifié, et de changer son pseudo sur le serveur discord.
    """

    return requests.post(
        "http://127.0.0.1:9814/verify",
        json={
            "discordId": discord_id,
            "pseudo": f"{identifiant}"
        },
        headers={"Authorization": "SECRET_KEY"}
    )
    

@auth.route('/register/step3', methods=['GET', 'POST'])    
def register_step3():
    if session.get('register_step', 1) < 2:
        return redirect(url_for('auth.register_step1'))
    elif session.get('register_step', 1) < 3:
        return redirect(url_for('auth.register_step2'))

    if request.method == 'POST':
        pseudo      = request.form.get('pseudo')
        identifiant = request.form.get('username')
        password    = generate_password_hash(
            request.form.get("password"),
            method="scrypt"
        )

        if pseudo and identifiant and password:
            # Récupérer les infos du bot Discord
            discord_id = session.get('discord-id')
            
            db = get_db()
            mycursor = db.cursor()
            
            # Insérer le membre dans la table Membre
            sql = ''' UPDATE Membre
                      SET nom_membre = %s,
                          mdp_membre = %s,
                          date_arrivee = %s,
                          role_id = %s,
                          nom_survivant = %s
                      WHERE id_membre = %s;'''
            
            date_arrivee = time.strftime('%Y-%m-%d %H:%M:%S')

            mycursor.execute(sql, (
                identifiant,
                password,
                date_arrivee,
                2,  # role_id par défaut pour un membre
                pseudo,
                discord_id
            ))

            db.commit()

            # Vérifier le membre sur Discord
            result = _verify(discord_id, identifiant)
            if result.status_code == 200:               # Réussite
                flash("Votre compte a bien été créé.", 'alert-warning')
            else :                                      # Échec
                flash("Votre compte a bien été créé. Mais impossible de marquer votre compte Discord comme vérifié. Alertez un administrateur.", 'alert-warning')

            session.pop('register_step', None)
            session.pop('discord-id', None)
            session.pop('session-id', None)

            return redirect(url_for('auth.auth_login'))
        
        else :
            flash("Le pseudo, l'identifiant ou le mot de passe n'ont pas été renseignés", 'alert-warning')
            return redirect("/register/step3")

    return render_template('auth/register/step3.html')