from Xlib.keysymdef.katakana import XK_kana_KA
from flask import Flask, request, render_template, redirect, flash, session, g, Blueprint
from connexion_db import get_db
from decorators import *
from function import auto_add_item_copy
import requests

membre_commandes = Blueprint('membre_commandes', __name__, template_folder='templates')


@membre_commandes.route('/membre/commandes')
@login_required
def show_membre_commandes():
    mycursor = get_db().cursor()

    sql = '''   SELECT Commande.id_commande,
                       Commande.date_achat,
                       SUM(Item_Copy.prix_item_copy * Ligne_Commande.quantite_commande) AS prix_commande,
                       SUM(Ligne_Commande.quantite_commande) AS quantite,
                       Etat.libelle_etat,
                       Commande.etat_id,
                       Carte.id_carte,
                       Carte.nom_carte
                       
                FROM Commande
                JOIN Ligne_Commande ON Ligne_Commande.commande_id = Commande.id_commande
                JOIN Item_Copy ON Item_Copy.id_item_copy = Ligne_Commande.item_copy_id
                JOIN Etat ON Etat.id_etat = Commande.etat_id
                JOIN Carte ON Carte.id_carte = Commande.carte_id
                
                WHERE Commande.membre_id = %s
                GROUP BY Commande.id_commande, date_achat
                ORDER BY Commande.date_achat DESC; '''
    mycursor.execute(sql, session['id_membre'])
    commandes = mycursor.fetchall()

    return render_template('membre/commandes/commandes.html', commandes=commandes)


@membre_commandes.route('/membre/commandes/details', methods=['GET'])
@login_required
def membre_commandes_details():

    id_commande = request.args.get('id_commande')
    mycursor = get_db().cursor()

    articles = []
    if id_commande != '':
        sql = ''' SELECT   Item_Copy.nom_item_copy,
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
    
                   WHERE Commande.membre_id = %s AND Commande.id_commande = %s; '''
        mycursor.execute(sql, (session['id_membre'], id_commande))
        articles = mycursor.fetchall()

    return render_template('/membre/commandes/_commandes.html', articles=articles)


@membre_commandes.route('/membre/commandes/add', methods=['POST'])
@login_required
def add_membre_commandes():

    mycursor = get_db().cursor()

    sql = ''' SELECT Ligne_Panier.sexe_id,
                     Ligne_Panier.item_id, 
                     Ligne_Panier.quantite_panier,
                     Ligne_Panier.sexe_id,
                     Item.prix_item,
                     Item.nom_item,
                     Item.image_item,
                     Item.type_item_id,
                     Item.commande_admin_item
                     
             FROM Ligne_Panier 
             JOIN Item ON Item.id_item = Ligne_Panier.item_id
             
             WHERE membre_id = %s; '''
    mycursor.execute(sql, (session['id_membre'],))
    lignes = mycursor.fetchall()

    if lignes:

        sql = ''' SELECT SUM(Ligne_Panier.quantite_panier * Item.prix_item) AS prix_total 
                  FROM Ligne_Panier 
                  JOIN Item ON Item.id_item = Ligne_Panier.item_id
                  WHERE Ligne_Panier.membre_id = %s; '''
        mycursor.execute(sql, (session['id_membre'],))
        prix_total = mycursor.fetchone()['prix_total']

        sql = ''' SELECT Membre.gold 
                  FROM Membre
                  WHERE id_membre = %s; '''
        mycursor.execute(sql, (session['id_membre'],))
        gold = mycursor.fetchone()['gold']

        if gold >= prix_total:
            id_carte = request.form.get('id_carte')

            sql = ''' UPDATE Membre
                      SET gold = gold - %s 
                      WHERE id_membre = %s; '''
            mycursor.execute(sql, (prix_total, session['id_membre']))

            sql = ''' INSERT INTO Commande(membre_id, date_achat, etat_id, carte_id) VALUES (%s, NOW(), %s, %s); '''
            mycursor.execute(sql, (session['id_membre'], 1, id_carte))

            id_commande = mycursor.lastrowid

            for ligne in lignes:

                id_item_copy = auto_add_item_copy(ligne)

                sql = ''' INSERT INTO Ligne_Commande(item_copy_id, commande_id, quantite_commande, sexe_id) VALUES (%s, %s, %s, %s); '''
                mycursor.execute(sql, (id_item_copy, id_commande, ligne['quantite_panier'], ligne['sexe_id']))

                sql = ''' DELETE FROM Ligne_Panier WHERE item_id = %s AND membre_id = %s AND sexe_id = %s; '''
                mycursor.execute(sql, (ligne['item_id'], session['id_membre'], ligne['sexe_id']))

                sql = ''' SELECT nom_carte,
                                 coo_boutique
                          FROM Carte 
                          WHERE id_carte = %s'''
                mycursor.execute(sql, (id_carte,))
                carte = mycursor.fetchone()

                # Message d'avertissement sur discord pour les admin
                message = f'''## Commande #{id_commande}
                              \n - Carte: **{carte['nom_carte']}**
                              \n - Membre: **{session['nom_membre']}**
                              \n - Coordonnées: **({carte['coo_boutique']})** '''

                # On envoie la requête
                result = requests.post(
                    "http://127.0.0.1:9814/send-msg",
                    json={
                        "channelId": 1525071044300378142,
                        "message": message
                    },
                    headers={"Authorization": "SECRET_KEY"}
                )

                # Message en mp pour le membre
                message = f'''Votre commande est confirmée ! Vous recevrez vos items dans votre coffre fort dès qu'un admin se sera occupé de votre commande. Mais ne vous inquiètez pas, je vous préviendrais dès que ce sera le cas :3
                              \n - ID Commande: **{id_commande}**
                              \n - Carte: **{carte['nom_carte']}**
                              \n - Coordonnées: **({carte['coo_boutique']})** '''

                # On envoie la requête
                result = requests.post(
                    "http://127.0.0.1:9814/send-dm",
                    json={
                        "discordId": session['id_membre'],
                        "message": message
                    },
                    headers={"Authorization": "SECRET_KEY"}
                )

                get_db().commit()

                # On agit dans le cas où la requête ne s'est pas bien passée et dans le cas où elle s'est bien passée
                if result.status_code != 200 :
                    flash(f"Une erreur est survenue lors de l'envoi du message dans le salon discord des admin.", 'alert-warning')

        else:
            flash("T'as pas les sous chef...")
            return redirect('/membre/panier')

    else:
        flash("Enregistrer un panier vide, c'est pas dans mes cordes...", 'alert-warning')

    return redirect('/membre/commandes')


@membre_commandes.route('/membre/commandes/cancel', methods=['POST'])
@login_required
def cancel_membre_commandes():
    id_commande = request.form['id_commande']
    id_membre = session['id_membre']

    mycursor = get_db().cursor()

    sql = ''' SELECT etat_id,
                     SUM(Item_Copy.prix_item_copy * Ligne_Commande.quantite_commande) AS prix_commande
                     
              FROM Ligne_Commande
              JOIN Commande ON Commande.id_commande = Ligne_Commande.commande_id
              JOIN Item_Copy ON Item_Copy.id_item_copy = Ligne_Commande.item_copy_id
              
              WHERE id_commande = %s
              AND membre_id = %s; '''
    mycursor.execute(sql, (id_commande, id_membre))
    commande = mycursor.fetchone()

    if commande:
        # Si l'état de la commande est autre chose que 'En attente d'un admin'
        if commande['etat_id'] != 1:
            flash('Vous ne pouvez pas annuler cette commande')

        else:
            sql = ''' UPDATE Commande SET etat_id = 4 WHERE id_commande = %s AND membre_id = %s; '''
            mycursor.execute(sql, (id_commande, id_membre))

            sql = ''' UPDATE Membre SET gold = gold + %s WHERE id_membre = %s; '''
            mycursor.execute(sql, (commande['prix_commande'], id_membre))

            get_db().commit()
            flash(f"Commande ID:{id_commande} annulée")

    else:
        flash('Commande introuvable')

    return redirect('/membre/commandes')