from flask import Flask, request, render_template, redirect, flash, session, g, Blueprint
from connexion_db import get_db
from decorators import *

admin = Blueprint('admin', __name__, template_folder='templates')


@admin.route('/admin')
@admin_required
def show_admin_menu():
    return render_template("admin/show_admin.html")


@admin.route('/admin/membre')
@admin_required
def show_membre():
    mycursor = get_db().cursor()
    sql = ''' SELECT Membre.id_membre,
                     Membre.nom_membre,
                     Membre.gold,
                     Role.libelle_role,
                     Membre.date_arrivee,
                     Membre.code_coffre,
                     Membre.dernier_claim,
                     Membre.nom_survivant 
              FROM Membre
              JOIN Role ON Role.id_role = Membre.role_id 
              ORDER BY Role.libelle_role DESC, Membre.date_arrivee DESC, Membre.nom_membre; '''
    mycursor.execute(sql)
    membres = mycursor.fetchall()

    return render_template("admin/membre/show_membre.html", membres=membres)


@admin.route('/admin/membre/edit', methods=['GET'])
@admin_required
def show_membre_edit():
    id_membre = request.args.get('id_membre', type=int)
    if not id_membre:
        flash("Membre introuvable.")
        return redirect('/admin/membre')

    mycursor = get_db().cursor()
    sql = ''' SELECT Membre.id_membre,
                     Membre.nom_membre,
                     Membre.gold,
                     Membre.role_id,
                     Role.libelle_role,
                     Membre.code_coffre,
                     Membre.nom_survivant,
                     Membre.date_arrivee,
                     Membre.dernier_claim
              FROM Membre
              JOIN Role ON Role.id_role = Membre.role_id
              WHERE Membre.id_membre = %s; '''
    mycursor.execute(sql, (id_membre,))
    membre = mycursor.fetchone()
    if not membre:
        flash("Membre introuvable.")
        return redirect('/admin/membre')

    sql = 'SELECT id_role, libelle_role FROM Role ORDER BY libelle_role;'
    mycursor.execute(sql)
    roles = mycursor.fetchall()

    return render_template('admin/membre/edit_membre.html', membre=membre, roles=roles)


@admin.route('/admin/membre/edit', methods=['POST'])
@admin_required
def valid_edit_membre():
    def normalize_nullable(value):
        if value is None:
            return None
        value = str(value).strip()
        if value == '' or value.lower() == 'none':
            return None
        return value

    id_membre = request.form.get('id_membre', type=int)
    nom_membre = normalize_nullable(request.form.get('nom_membre'))
    gold = request.form.get('gold', type=int)
    role_id = request.form.get('role_id', type=int)
    code_coffre = normalize_nullable(request.form.get('code_coffre'))
    nom_survivant = normalize_nullable(request.form.get('nom_survivant'))

    if not id_membre or gold is None or role_id is None or code_coffre is None:
        flash("Gold, rôle et code de coffre sont obligatoires.")
        return redirect(f'/admin/membre/edit?id_membre={id_membre}')

    mycursor = get_db().cursor()
    sql = ''' UPDATE Membre
              SET nom_membre = %s,
                  gold = %s,
                  role_id = %s,
                  code_coffre = %s,
                  nom_survivant = %s
              WHERE id_membre = %s; '''
    mycursor.execute(sql, (nom_membre, gold, role_id, code_coffre, nom_survivant, id_membre))
    get_db().commit()

    flash("Informations du membre mises à jour.")
    return redirect('/admin/membre')


@admin.route('/admin/article')
@admin_required
def show_article():
    mycursor = get_db().cursor()
    sql = ''' SELECT * FROM Espece WHERE taming = %s ORDER BY id_espece; '''
    mycursor.execute(sql, 1)
    especes = mycursor.fetchall()
    return render_template("admin/show_article.html", especes=especes)


@admin.route('/admin/article/edit', methods=['POST'])
@admin_required
def edit_article():

    multiplicateur = request.form.get('multiplicateur', type=float)
    valeur = request.form.get('valeur', type=int)
    especes_ids = request.form.getlist('especes')

    if not especes_ids:
        flash("Aucune espèce sélectionnée.")
        return redirect('/admin/article')

    if not multiplicateur and not valeur:
        flash("Remplissez au moins un modificateur !")
        return redirect('/admin/article')

    if multiplicateur and valeur:
        flash("Utilisez soit un multiplicateur soit une valeur, pas les deux.")
        return redirect('/admin/article')

    placeholders = ','.join(['%s'] * len(especes_ids))

    mycursor = get_db().cursor()

    if multiplicateur:
        sql = f"""
            UPDATE Espece
            SET prix_espece = prix_espece * %s
            WHERE id_espece IN ({placeholders})
        """
        mycursor.execute(sql, [multiplicateur] + especes_ids)

    elif valeur:
        sql = f"""
            UPDATE Espece
            SET prix_espece = prix_espece + %s
            WHERE id_espece IN ({placeholders})
        """
        mycursor.execute(sql, [valeur] + especes_ids)

    placeholders = ",".join(["%s"] * len(especes_ids))
    sql = f"""
            SELECT id_article
            FROM Article
            WHERE nom_article IN
            (
                SELECT nom_espece
                FROM Espece
                WHERE id_espece IN ({placeholders})
            )
    """
    mycursor.execute(sql, especes_ids)
    articles_ids = mycursor.fetchall()

    if articles_ids:
        articles_ids = [row['id_article'] for row in articles_ids]

        placeholders = ",".join(["%s"] * len(articles_ids))
        sql = f"DELETE FROM Ligne_Panier WHERE article_id IN ({placeholders})"
        mycursor.execute(sql, articles_ids)

    get_db().commit()

    flash("Modification appliquée avec succès.")
    return redirect('/admin/article')