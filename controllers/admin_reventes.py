from Xlib.keysymdef.katakana import XK_kana_KA
from flask import Flask, request, render_template, redirect, flash, session, g, Blueprint
from connexion_db import get_db
from decorators import *
from function import *
import requests

admin_reventes = Blueprint('admin_reventes', __name__, template_folder='templates')


@admin_reventes.route('/admin/reventes')
@admin_required
def show_admin_reventes():
    mycursor = get_db().cursor()

    sql = '''   SELECT Revente.id_revente,
                       Revente.date_revente,
                       SUM(Item_Copy.prix_item_copy * Ligne_Revente.quantite_revente) AS prix_revente,
                       SUM(Ligne_Revente.quantite_revente) AS quantite,
                       Revente.etat_id,
                       Etat.libelle_etat,
                       Carte.id_carte,
                       Carte.nom_carte,
                       Membre.nom_membre

                FROM Revente
                JOIN Ligne_Revente ON Ligne_Revente.revente_id = Revente.id_revente
                JOIN Item_Copy ON Item_Copy.id_item_copy = Ligne_Revente.item_copy_id
                JOIN Etat ON Etat.id_etat = Revente.etat_id
                JOIN Carte ON Carte.id_carte = Revente.carte_id
                JOIN Membre ON Membre.id_membre = Revente.membre_id

                GROUP BY Revente.id_revente, Revente.date_revente
                ORDER BY Revente.etat_id, Revente.date_revente DESC; '''
    mycursor.execute(sql)
    reventes = mycursor.fetchall()

    return render_template('admin/reventes/show_reventes.html', reventes=reventes, articles=[])


@admin_reventes.route('/admin/reventes/details', methods=['GET'])
@login_required
def membre_reventes_details():
    mycursor = get_db().cursor()

    id_revente = request.args.get('id_revente')
    articles = []

    if id_revente != '':
        sql = ''' SELECT       Revente.id_revente,
                               Item_Copy.nom_item_copy,
                               Item_Copy.type_item_id,
                               Item_Copy.commande_admin_item_copy,
                               Item_Copy.image_item_copy, 

                               Type_Item.nom_type_item,
                               (Item_Copy.prix_item_copy * Ligne_Revente.quantite_revente) AS prix_revente,
                               Ligne_Revente.quantite_revente AS quantite

                       FROM Ligne_Revente
                       JOIN Revente ON Revente.id_revente = Ligne_Revente.revente_id
                       JOIN Item_Copy ON Item_Copy.id_item_copy = Ligne_Revente.item_copy_id
                       JOIN Type_Item ON Type_Item.id_type_item = Item_Copy.type_item_id

                       WHERE Revente.id_revente = %s; '''
        mycursor.execute(sql, (id_revente,))
        articles = mycursor.fetchall()

        for article in articles:
            article['commande_admin_item_copy'] = get_admin_cmd(article)

    return render_template('/admin/reventes/_show_details.html', articles=articles)


@admin_reventes.route('/admin/reventes/valid', methods=['POST'])
@admin_required
def valid_admin_reventes():
    id_revente = request.form['id_revente']

    # Correspond à une commande accomplie
    new_id_etat = 2

    mycursor = get_db().cursor()

    sql = ''' SELECT membre_id,
                     SUM(Item_Copy.prix_item_copy * Ligne_Revente.quantite_revente) AS prix_revente,
                     etat_id
              FROM Revente
              JOIN Ligne_Revente ON Ligne_Revente.revente_id = Revente.id_revente
              JOIN Item_Copy ON Item_Copy.id_item_copy = Ligne_Revente.item_copy_id

              WHERE id_revente = %s; '''
    mycursor.execute(sql, (id_revente,))
    revente = mycursor.fetchone()

    if revente and revente['etat_id'] == 1:
        sql = ''' UPDATE Revente SET etat_id = %s WHERE id_revente = %s; '''
        mycursor.execute(sql, (new_id_etat, id_revente))

        sql = ''' UPDATE Membre SET gold = gold + %s WHERE id_membre = %s; '''
        mycursor.execute(sql, (revente['prix_revente'], revente['membre_id']))

        flash(f'Revente ID:{id_revente} validée, le Membre a bien reçu ses Gold')

        # Envoi du message au membre pour le prévenir
        message = f'''Vous avez bien reçu les **{revente['prix_revente']}** Gold de votre commande (ID:{id_revente}).'''

        # On envoie la requête
        result = requests.post(
            "http://127.0.0.1:9814/send-dm",
            json={
                "discordId": session['id_membre'],
                "message": message
            },
            headers={"Authorization": "SECRET_KEY"}
        )

        # On agis dans le cas où la requête ne s'est pas bien passée et dans le cas où elle s'est bien passée
        if result.status_code != 200:
            flash("Une erreur est survenue lors de l'envoi du message à l'utilisateur.", 'alert-warning')

        get_db().commit()

    else:
        flash('Opération incorrecte')

    return redirect('/admin/reventes')


@admin_reventes.route('/admin/reventes/cancel', methods=['POST'])
@admin_required
def cancel_admin_reventes():

    id_revente = request.form['id_revente']

    # Correspond à une commande accomplie
    new_id_etat = 3

    mycursor = get_db().cursor()

    sql = ''' SELECT membre_id,
                     SUM(Item_Copy.prix_item_copy * Ligne_Revente.quantite_revente) AS prix_revente,
                     etat_id
              FROM Revente
              JOIN Ligne_Revente ON Ligne_Revente.revente_id = Revente.id_revente
              JOIN Item_Copy ON Item_Copy.id_item_copy = Ligne_Revente.item_copy_id

              WHERE id_revente = %s; '''
    mycursor.execute(sql, (id_revente,))
    revente = mycursor.fetchone()

    if revente and revente['etat_id'] == 1:
        sql = ''' UPDATE Revente SET etat_id = %s WHERE id_revente = %s; '''
        mycursor.execute(sql, (new_id_etat, id_revente))

        flash(f'Revente ID:{id_revente} annulée')
        get_db().commit()

    else:
        flash('Opération incorrecte')

    return redirect('/admin/reventes')