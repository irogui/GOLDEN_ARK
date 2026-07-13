from Xlib.keysymdef.katakana import XK_kana_KA
from flask import Flask, request, render_template, redirect, flash, session, g, Blueprint
from connexion_db import get_db
from decorators import *
from function import *
import requests

admin_commandes = Blueprint('admin_commandes', __name__, template_folder='templates')


@admin_commandes.route('/admin/commandes')
@admin_required
def show_admin_commandes():
    mycursor = get_db().cursor()

    sql = '''   SELECT Commande.id_commande,
                       Commande.date_achat,
                       SUM(Item_Copy.prix_item_copy * Ligne_Commande.quantite_commande) AS prix_commande,
                       SUM(Ligne_Commande.quantite_commande) AS quantite,
                       Commande.etat_id,
                       Etat.libelle_etat,
                       Carte.id_carte,
                       Carte.nom_carte,
                       Membre.nom_membre,
                       Membre.code_coffre
        
                FROM Commande
                JOIN Ligne_Commande ON Ligne_Commande.commande_id = Commande.id_commande
                JOIN Item_Copy ON Item_Copy.id_item_copy = Ligne_Commande.item_copy_id
                JOIN Etat ON Etat.id_etat = Commande.etat_id
                JOIN Carte ON Carte.id_carte = Commande.carte_id
                JOIN Membre ON Membre.id_membre = Commande.membre_id
        
                GROUP BY Commande.id_commande, date_achat
                ORDER BY Commande.etat_id, Commande.date_achat DESC; '''
    mycursor.execute(sql)
    commandes = mycursor.fetchall()

    return render_template('admin/commandes/show_commandes.html', commandes=commandes, articles=[])


@admin_commandes.route('/admin/commandes/details', methods=['GET'])
@login_required
def membre_commandes_details():

    mycursor = get_db().cursor()

    id_commande = request.args.get('id_commande')
    articles = []

    if id_commande != '':
        sql = ''' SELECT       Commande.id_commande,
                               Item_Copy.nom_item_copy,
                               Item_Copy.type_item_id,
                               Item_Copy.commande_admin_item_copy,
                               Item_Copy.image_item_copy, 

                               Type_Item.nom_type_item,
                               (Item_Copy.prix_item_copy * Ligne_Commande.quantite_commande) AS prix_commande,
                               Ligne_Commande.quantite_commande AS quantite,
                               Sexe.id_sexe,
                               Sexe.libelle_sexe

                       FROM Ligne_Commande
                       JOIN Commande ON Commande.id_commande = Ligne_Commande.commande_id
                       JOIN Item_Copy ON Item_Copy.id_item_copy = Ligne_Commande.item_copy_id
                       JOIN Type_Item ON Type_Item.id_type_item = Item_Copy.type_item_id
                       JOIN Sexe ON Sexe.id_sexe = Ligne_Commande.sexe_id

                       WHERE Commande.id_commande = %s; '''
        mycursor.execute(sql, (id_commande,))
        articles = mycursor.fetchall()

        for article in articles:
            article['commande_admin_item_copy'] = get_admin_cmd(article)

    return render_template('/admin/commandes/_show_details.html', articles=articles)



@admin_commandes.route('/admin/commandes/valid', methods=['POST'])
@admin_required
def valid_admin_commandes():
    id_commande = request.form['id_commande']

    # Correspond à une commande accomplie
    new_id_etat = 2

    mycursor = get_db().cursor()

    sql = ''' SELECT membre_id,
                     SUM(Item_Copy.prix_item_copy * Ligne_Commande.quantite_commande) AS prix_commande,
                     Commande.etat_id,
                     Carte.nom_carte AS nom_carte,
                     Carte.coo_boutique AS coo_boutique
              FROM Commande
              JOIN Ligne_Commande ON Ligne_Commande.commande_id = Commande.id_commande
              JOIN Item_Copy ON Item_Copy.id_item_copy = Ligne_Commande.item_copy_id
              JOIN Carte ON Carte.id_carte = Commande.carte_id

              WHERE id_commande = %s; '''
    mycursor.execute(sql, (id_commande,))
    commande = mycursor.fetchone()

    if commande and commande['etat_id'] == 1:
        sql = ''' UPDATE Commande SET etat_id = %s WHERE id_commande = %s; '''
        mycursor.execute(sql, (new_id_etat, id_commande))

        flash(f'Commande ID:{id_commande} validée')

        message = f"La livraison de votre Commande **ID:{id_commande}** a été effectuée. Vous pouvez retrouver vos items sur **{commande['nom_carte']}** aux coordonnées suivantes : **({commande['coo_boutique']})**. Les éléments commandés seront stockés dans un coffre fort dont le code, lié à votre compte, se trouve sur le site internet."

        # On envoie la requête
        result = requests.post(
            "http://127.0.0.1:9814/send-dm",
            json={
                "discordId": commande["membre_id"],
                "message": message
            },
            headers={"Authorization": "SECRET_KEY"}
        )

        # On agis dans le cas où la requête ne s'est pas bien passée et dans le cas où elle s'est bien passée
        if result.status_code != 200 :
            flash("Une erreur est survenue lors de l'envoi du message à l'utilisateur.", 'alert-warning')

        get_db().commit()

    else:
        flash('Opération incorrecte')

    return redirect('/admin/commandes')


@admin_commandes.route('/admin/commandes/cancel', methods=['POST'])
@admin_required
def cancel_admin_commandes():

    id_commande = request.form['id_commande']

    # Correspond à une commande accomplie
    new_id_etat = 3

    mycursor = get_db().cursor()

    sql = ''' SELECT membre_id,
                     SUM(Item_Copy.prix_item_copy * Ligne_Commande.quantite_commande) AS prix_commande,
                     etat_id
              FROM Commande
              JOIN Ligne_Commande ON Ligne_Commande.commande_id = Commande.id_commande
              JOIN Item_Copy ON Item_Copy.id_item_copy = Ligne_Commande.item_copy_id

              WHERE id_commande = %s; '''
    mycursor.execute(sql, (id_commande,))
    commande = mycursor.fetchone()

    if commande and commande['etat_id'] == 1:
        sql = ''' UPDATE Commande SET etat_id = %s WHERE id_commande = %s; '''
        mycursor.execute(sql, (new_id_etat, id_commande))

        sql = ''' UPDATE Membre SET gold = gold + %s WHERE id_membre = %s; '''
        mycursor.execute(sql, (commande['prix_commande'], commande['membre_id']))

        flash(f'Commande ID:{id_commande} annulée, Membre remboursé')

        message = f"La livraison de votre Commande **ID:{id_commande}** a été annulée. Pour plus de détails, veuillez contacter un administrateur."

        # On envoie la requête
        result = requests.post(
            "http://127.0.0.1:9814/send-dm",
            json={
                "discordId": commande["membre_id"],
                "message": message
            },
            headers={"Authorization": "SECRET_KEY"}
        )

        # On agis dans le cas où la requête ne s'est pas bien passée et dans le cas où elle s'est bien passée
        if result.status_code != 200 :
            flash("Une erreur est survenue lors de l'envoi du message à l'utilisateur.", 'alert-warning')

        get_db().commit()

    else:
        flash('Opération incorrecte')

    return redirect('/admin/commandes')