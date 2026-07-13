from flask import Flask, request, render_template, redirect, flash, session, g, Blueprint
from connexion_db import get_db
from decorators import *
from function import *
import requests


membre_reventes = Blueprint('membre_reventes', __name__, template_folder='templates')


def get_table_trophes(template: str) -> None:
    ''' Renvoi le template mit en argmument avec en variables injectées:
        - plafond restant
        - total des valeurs de trophées selectionnés
        - trophées vendables (dont ceux sélectionnés)
        - les cartes disponibles sur le serveur.

        Cette fonction a pour but de charger la page add_reventes.html sans de voir répéter les mêmes requêtes SQL à chaque fois '''

    plafond_revente = get_plafond_revente(session['id_membre'])

    mycursor = get_db().cursor()

    sql = ''' SELECT Item.id_item,
                         Item.nom_item,
                         Item.image_item,
                         Item.prix_item,
                         IFNULL(Ligne_Trophe.quantite_trophe, 0) AS quantite_trophe

                  FROM Trophe
                  JOIN Item ON Item.id_item = Trophe.id_item
                  LEFT JOIN Ligne_Trophe ON Ligne_Trophe.item_id = Trophe.id_item

                  ORDER BY quantite_trophe DESC, nom_item; '''
    mycursor.execute(sql)
    trophes = mycursor.fetchall()

    sql = ''' SELECT SUM(Ligne_Trophe.quantite_trophe * Item.prix_item) AS total_vente
                  FROM Ligne_Trophe
                  JOIN Item ON Item.id_item = Ligne_Trophe.item_id
                  WHERE Ligne_Trophe.membre_id = %s; '''
    mycursor.execute(sql, (session['id_membre'],))
    result = mycursor.fetchone()
    total_vente = result['total_vente'] if result['total_vente'] else 0

    sql = ''' SELECT id_carte,
                         nom_carte
                  FROM Carte 
                  WHERE dispo_carte; '''
    mycursor.execute(sql)
    cartes = mycursor.fetchall()

    return render_template(template, plafond_revente=plafond_revente, total_vente=total_vente, trophes=trophes, cartes=cartes)



@membre_reventes.route('/membre/reventes')
@login_required
def show_reventes():
    mycursor = get_db().cursor()

    sql = '''   SELECT Revente.id_revente,
                       Revente.date_revente,
                       Revente.etat_id,
                       Etat.libelle_etat,
                       Carte.id_carte,
                       Carte.nom_carte,
                       SUM(Item_Copy.prix_item_copy * Ligne_Revente.quantite_revente) AS prix_revente,
                       SUM(Ligne_Revente.quantite_revente) AS quantite
    
                FROM Revente
                JOIN Ligne_Revente ON Ligne_Revente.revente_id = Revente.id_revente
                JOIN Item_Copy ON Item_Copy.id_item_copy = Ligne_Revente.item_copy_id
                JOIN Etat ON Etat.id_etat = Revente.etat_id
                JOIN Carte ON Carte.id_carte = Revente.carte_id
    
                WHERE Revente.membre_id = %s
                GROUP BY Revente.id_revente, Revente.date_revente
                ORDER BY Revente.date_revente DESC; '''
    mycursor.execute(sql, session['id_membre'])
    reventes = mycursor.fetchall()

    return render_template("/membre/reventes/show_reventes.html", reventes=reventes)


@membre_reventes.route('/membre/reventes/details', methods=['GET'])
@login_required
def membre_reventes_details():

    id_revente = request.args.get('id_revente')

    mycursor = get_db().cursor()

    articles = []

    if id_revente != '':
        sql = '''  SELECT Item_Copy.nom_item_copy,
                           Item_Copy.image_item_copy, 
                           Type_Item.nom_type_item,
                           (Item_Copy.prix_item_copy * Ligne_Revente.quantite_revente) AS prix_revente,
                           Ligne_Revente.quantite_revente AS quantite

                      FROM Ligne_Revente
                      JOIN Revente ON Revente.id_revente = Ligne_Revente.revente_id
                      JOIN Item_Copy ON Item_Copy.id_item_copy = Ligne_Revente.item_copy_id
                      JOIN Type_Item ON Type_Item.id_type_item = Item_Copy.type_item_id

                      WHERE Revente.membre_id = %s AND Revente.id_revente = %s; '''
        mycursor.execute(sql, (session['id_membre'], id_revente))
        articles = mycursor.fetchall()

    return render_template('/membre/reventes/_show_reventes.html', articles=articles)


@membre_reventes.route('/membre/reventes/add', methods=['GET'])
@login_required
def add_reventes():

    return get_table_trophes('/membre/reventes/add_reventes.html')


@membre_reventes.route('/membre/reventes/add', methods=['POST'])
@login_required
def valid_add_reventes():

    id_item = request.form.get('id_item')
    quantite_voulue = int(request.form.get('quantite_voulue'))
    prix_item = int(request.form.get('prix_item'))
    total_vente = int(request.form.get('total_vente'))

    mycursor = get_db().cursor()

    # Vérification de l'existence de l'item d'id 'item_id' déjà présent dans Ligne_Trophe de ce membre
    sql = ''' SELECT item_id,
                     quantite_trophe
                     
              FROM Ligne_Trophe
              JOIN Item ON Item.id_item = Ligne_Trophe.item_id
              
              WHERE Ligne_Trophe.membre_id = %s AND Item.id_item = %s; '''
    mycursor.execute(sql, (session['id_membre'], id_item))
    ligne = mycursor.fetchone()

    plafond_revente = get_plafond_revente(session['id_membre'])

    # Demande-moi bebou, jte jure que ce sera plus simple que de prendre 10 lignes pour l'expliquer ;3
    total_vente -= (ligne['quantite_trophe'] * prix_item) if ligne else 0

    # Si jamais la quantité saisie créée un dépassement du plafond, il y a alors un calcul de quantite_voulue pour qu'il ait la plus haute valeur possible
    if total_vente + (quantite_voulue * prix_item) > plafond_revente:
        quantite_voulue = (plafond_revente - total_vente) // prix_item
        flash('Plafond déjà atteint !')

    if ligne:
        if quantite_voulue > 0:
            sql = ''' UPDATE Ligne_Trophe SET quantite_trophe = %s WHERE membre_id = %s AND item_id = %s; '''
            mycursor.execute(sql, (quantite_voulue, session['id_membre'], id_item))
        else:
            sql = ''' DELETE FROM Ligne_Trophe WHERE membre_id = %s AND item_id = %s; '''
            mycursor.execute(sql, (session['id_membre'], id_item))

    else:
        sql = ''' INSERT INTO Ligne_Trophe(membre_id, item_id, quantite_trophe) VALUES (%s, %s, %s); '''
        mycursor.execute(sql, (session['id_membre'], id_item, quantite_voulue))

    get_db().commit()
    return get_table_trophes('/membre/reventes/_add_reventes.html')


@membre_reventes.route('/membre/reventes/valid', methods=['POST'])
@login_required
def valid_reventes():
    plafond_revente = get_plafond_revente(session['id_membre'])

    if plafond_revente > 0:
        mycursor = get_db().cursor()

        sql = ''' SELECT Ligne_Trophe.item_id,
                         Ligne_Trophe.membre_id,
                         Ligne_Trophe.quantite_trophe,
                         
                         Item.nom_item,
                         Item.prix_item,
                         Item.image_item,
                         Item.type_item_id,
                         Item.commande_admin_item
                         
                  FROM Ligne_Trophe
                  JOIN Item ON Item.id_item = Ligne_Trophe.item_id
                  
                  WHERE membre_id = %s; '''
        mycursor.execute(sql, (session['id_membre'],))
        lignes = mycursor.fetchall()

        if lignes:
            id_carte = request.form.get('id_carte')

            sql = ''' INSERT INTO Revente(membre_id, date_revente, etat_id, carte_id) VALUES (%s, NOW(), %s, %s); '''
            mycursor.execute(sql, (session['id_membre'], 1, id_carte))

            id_revente = mycursor.lastrowid

            for ligne in lignes:

                id_item_copy = auto_add_item_copy(ligne)

                sql = ''' INSERT INTO Ligne_Revente(item_copy_id, revente_id, quantite_revente) VALUES (%s, %s, %s); '''
                mycursor.execute(sql, (id_item_copy, id_revente, ligne['quantite_trophe']))

                sql = ''' DELETE FROM Ligne_Trophe WHERE item_id = %s AND membre_id = %s; '''
                mycursor.execute(sql, (ligne['item_id'], session['id_membre']))


            # Récupération des info de la carte
            sql = ''' SELECT nom_carte,
                             coo_boutique
                      FROM Carte 
                      WHERE id_carte = %s'''
            mycursor.execute(sql, (id_carte,))
            carte = mycursor.fetchone()

            # Récupération du code de coffre du membre
            sql = ''' SELECT code_coffre
                      FROM Membre
                      WHERE id_membre = %s; '''
            mycursor.execute(sql, (session['id_membre'],))
            code_coffre = mycursor.fetchone()['code_coffre']

            # Message d'avertissement sur discord pour les admin
            message = f'''## Revente #{id_revente}
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
            message = f'''Votre revente est confirmée ! Assurez-vous d'avoir déposé le bon nombre d'items dans votre coffre fort.
                      \n - ID Commande: **{id_revente}**
                      \n - Carte: **{carte['nom_carte']}**
                      \n - Coordonnées: **({carte['coo_boutique']})**
                      \n - Code Coffre: **[{code_coffre}]**'''

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
            if result.status_code != 200:
                flash(f"Une erreur est survenue lors de l'envoi du message dans le salon discord des admin.",
                      'alert-warning')

            get_db().commit()

            flash('La revente a bien été prise en compte')
            return redirect('/membre/reventes')

        else:
            flash("Tu n'as encore entré aucun trophé !", 'alert-warning')
            return redirect('/membre/reventes/add')

    else:
        flash(f"Temps restant: {get_temps_restant(session['id_membre'])} avant la recouverture du plafond")
        return redirect('/membre/reventes/add')


@membre_reventes.route('/membre/reventes/delete/all', methods=['GET'])
@login_required
def delete_all_reventes():
    mycursor = get_db().cursor()
    sql = ''' DELETE FROM Ligne_Trophe WHERE membre_id = %s; '''
    mycursor.execute(sql, (session['id_membre'],))
    get_db().commit()
    flash('Votre tableau a été vidé')
    return redirect('/membre/reventes/add')


@membre_reventes.route('/membre/reventes/cancel', methods=['POST'])
@login_required
def cancel_membre_reventes():
    id_revente = request.form['id_revente']
    id_membre = session['id_membre']

    mycursor = get_db().cursor()

    sql = ''' SELECT etat_id
              FROM Revente
              WHERE id_revente = %s
              AND membre_id = %s; '''
    mycursor.execute(sql, (id_revente, id_membre))
    revente = mycursor.fetchone()

    if revente:
        # Si l'état de la revente est autre chose que 'En attente d'un admin'
        if revente['etat_id'] != 1:
            flash('Vous ne pouvez pas annuler cette revente')

        else:
            sql = ''' UPDATE Revente SET etat_id = 4 WHERE id_revente = %s AND membre_id = %s; '''
            mycursor.execute(sql, (id_revente, id_membre))

            get_db().commit()
            flash(f"Revente ID:{id_revente} annulée")

    else:
        flash('Revente introuvable')

    return redirect('/membre/reventes')