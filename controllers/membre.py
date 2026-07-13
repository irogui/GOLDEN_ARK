from flask import Flask, request, render_template, redirect, flash, session, g, Blueprint
from connexion_db import get_db
from decorators import *
import os
import requests
from werkzeug.security import generate_password_hash

membre = Blueprint('membre', __name__, template_folder='templates')
IMG_FORMATS = ("jpg", "jpeg", "jfif", "png", "gif", "webp", "avif")

def _check_pfp_exists(discordId: int) -> str | None:
    for ext in IMG_FORMATS:
        path = f"./static/images/membres/{discordId}.{ext}"
        if os.path.exists(path):
            return path
    return None


def _save_avatar(url: str, filename: str) -> str:
    response = requests.get(url)
    response.raise_for_status()

    with open(filename, "wb") as f:
        f.write(response.content)

    return filename


def _extract_extension(url: str) -> str:
    # On enlève les paramètres ?size=1024
    clean = url.split("?")[0]
    ext = clean.split(".")[-1].lower()
    return ext



@membre.route('/membre')
@login_required
def show_membre():
    discordId = session['id_membre']

    mycursor = get_db().cursor()

    sql = ''' SELECT Membre.id_membre,
                     Membre.nom_membre,
                     Membre.nom_survivant,
                     Membre.gold,
                     Membre.code_coffre,
                     
                     Role.id_role,
                     Role.libelle_role,
                     
                     COUNT(id_commande) AS nb_commandes,
                     COUNT(id_revente) AS nb_reventes
                     
              FROM Membre
              JOIN Role ON Role.id_role = Membre.role_id
              LEFT JOIN Commande ON Commande.membre_id = Membre.id_membre
              LEFT JOIN Revente ON Revente.membre_id = Membre.id_membre
              
              WHERE Membre.id_membre = %s
              
              GROUP BY Membre.id_membre, Membre.nom_membre, Membre.gold, Role.id_role, Role.libelle_role; '''
    mycursor.execute(sql, discordId)
    membre = mycursor.fetchone()

    # Vérifier si la PFP existe déjà
    path = _check_pfp_exists(discordId)

    if not path:
        # Requête au bot
        result = requests.post(
            "http://127.0.0.1:9814/pfp",
            json={"discordId": discordId},
            headers={"Authorization": "SECRET_KEY"}
        )

        if result.status_code != 200:
            print(result.content.decode("utf-8"))
            flash("Une erreur est survenue, impossible de récupérer votre photo de profil Discord.", 'alert-warning')
        else:
            data = result.json()
            url = data.get("url")

            if not url:
                flash("Impossible de récupérer votre photo de profil Discord.", 'alert-warning')
            else:
                # Extraire l'extension
                ext = _extract_extension(url)

                # Construire le chemin final
                filename = f"./static/images/membres/{discordId}.{ext}"

                # Télécharger et sauvegarder
                _save_avatar(url, filename)

                path = filename  # maintenant il existe

    # Chemin relatif pour le template
    pfp_rel = path.replace("./static/", "/static/")

    return render_template('membre/membre.html', membre=membre, pfp=pfp_rel)


@membre.route('/membre/modify', methods=['GET'])
@login_required
def show_membre_modify():
    discordId = session['id_membre']
    mycursor = get_db().cursor()
    sql = ''' SELECT Membre.id_membre,
                     Membre.nom_membre,
                     Membre.nom_survivant
              FROM Membre
              WHERE Membre.id_membre = %s; '''
    mycursor.execute(sql, (discordId,))
    membre_data = mycursor.fetchone()
    if not membre_data:
        flash("Impossible de charger vos informations.", 'alert-warning')
        return redirect('/membre')

    return render_template('membre/modify_membre.html', membre=membre_data)


@membre.route('/membre/modify', methods=['POST'])
@login_required
def valid_membre_modify():
    discordId = session['id_membre']
    nom_membre = request.form.get('nom_membre', '').strip()
    nom_survivant = request.form.get('nom_survivant', '').strip()
    password = request.form.get('password', '').strip()

    if nom_membre.lower() == 'none' or nom_survivant.lower() == 'none':
        flash("Le nom du membre et le nom de survivant ne peuvent pas être 'None'.", 'alert-warning')
        return redirect('/membre/modify')

    if not nom_membre or not nom_survivant:
        flash("Le nom du membre et le nom de survivant sont obligatoires.", 'alert-warning')
        return redirect('/membre/modify')

    if password:
        password = generate_password_hash(password, method='scrypt')

    sql_parts = [
        'nom_membre = %s',
        'nom_survivant = %s'
    ]
    params = [nom_membre, nom_survivant]

    if password:
        sql_parts.append('mdp_membre = %s')
        params.append(password)

    params.append(discordId)

    sql = f"UPDATE Membre SET {', '.join(sql_parts)} WHERE id_membre = %s;"
    mycursor = get_db().cursor()
    mycursor.execute(sql, params)

    session['nom_membre'] = nom_membre
    get_db().commit()

    flash("Vos informations ont été mises à jour.", 'alert-warning')
    return redirect('/membre')
