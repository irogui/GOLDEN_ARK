from flask import Flask, request, render_template, redirect, flash, session, g, Blueprint
from connexion_db import get_db
from decorators import *
from function import *

membre_panier = Blueprint('membre_panier', __name__, template_folder='templates')


def refresh_panier():
    ''' Fonction permettant de refresh la page panier de façon dynamique '''

    mycursor = get_db().cursor()

    sql = ''' SELECT Ligne_Panier.membre_id,
                     Item.id_item,
                     Item.nom_item,
                     Item.image_item,
                     Type_Item.id_type_item,
                     Type_Item.nom_type_item,
                     Ligne_Panier.quantite_panier,
                     (Item.prix_item * Ligne_Panier.quantite_panier) AS prix_ligne,
                     Sexe.id_sexe,
                     Sexe.libelle_sexe                     
    
                  FROM Ligne_Panier
                  JOIN Item ON Item.id_item = Ligne_Panier.item_id
                  JOIN Type_Item ON Type_Item.id_type_item = Item.type_item_id
                  LEFT JOIN Sexe ON Sexe.id_sexe = Ligne_Panier.sexe_id 
    
                  WHERE Ligne_Panier.membre_id = %s
                  ORDER BY Item.id_item, Sexe.id_sexe; '''
    mycursor.execute(sql, session['id_membre'])
    items = mycursor.fetchall()

    sql = ''' SELECT SUM(Item.prix_item * Ligne_Panier.quantite_panier) AS prix_total
              FROM Ligne_Panier
              JOIN Item ON Item.id_item = Ligne_Panier.item_id 
              WHERE Ligne_Panier.membre_id = %s; '''
    mycursor.execute(sql, session['id_membre'])
    prix_total = mycursor.fetchone()

    cartes = get_maps()

    return render_template('/membre/panier/_panier.html', items=items, prix_total=prix_total, cartes=cartes)


def get_maps() -> dict:
    ''' Renvoi toutes les cartes disponibles dans laquelle l'item, s'il est une créature peut apparaître naturellement.
        Fjordur faisant exception car est la carte principale. '''
    mycursor = get_db().cursor()

    sql = '''
            SELECT DISTINCT (Carte.id_carte), 
                   Carte.nom_carte
                   
            FROM Carte 
            WHERE Carte.dispo_carte AND 
            (NOT EXISTS (
                
                SELECT 1
                FROM Ligne_Panier
                JOIN Item ON Item.id_item = Ligne_Panier.item_id
                
                WHERE Ligne_Panier.membre_id = %s
                AND Item.type_item_id = 1
                
                AND Item.id_item NOT IN (
                    SELECT Apparition.espece_id
                    FROM Apparition
                    WHERE Apparition.carte_id = Carte.id_carte
                )
            )
            
            OR Carte.id_carte = 12); '''
    mycursor.execute(sql, (session['id_membre']))
    cartes = mycursor.fetchall()

    return cartes



@membre_panier.route('/membre/panier')
@login_required
def show_panier():
    mycursor = get_db().cursor()
    get_maps()
    sql = ''' SELECT Ligne_Panier.membre_id,
                     Item.id_item,
                     Item.nom_item,
                     Item.image_item,
                     Type_Item.id_type_item,
                     Type_Item.nom_type_item,
                     Ligne_Panier.quantite_panier,
                     (Item.prix_item * Ligne_Panier.quantite_panier) AS prix_ligne,
                     Sexe.id_sexe,
                     Sexe.libelle_sexe                     

              FROM Ligne_Panier
              JOIN Item ON Item.id_item = Ligne_Panier.item_id
              JOIN Type_Item ON Type_Item.id_type_item = Item.type_item_id
              LEFT JOIN Sexe ON Sexe.id_sexe = Ligne_Panier.sexe_id 

              WHERE Ligne_Panier.membre_id = %s
              ORDER BY Item.id_item, Sexe.id_sexe; '''
    mycursor.execute(sql, session['id_membre'])
    items = mycursor.fetchall()

    sql = ''' SELECT SUM(Item.prix_item * Ligne_Panier.quantite_panier) AS prix_total
              FROM Ligne_Panier
              JOIN Item ON Item.id_item = Ligne_Panier.item_id 
              WHERE Ligne_Panier.membre_id = %s; '''
    mycursor.execute(sql, session['id_membre'])
    prix_total = mycursor.fetchone()

    cartes = get_maps()

    return render_template('membre/panier/panier.html', items=items, prix_total=prix_total, cartes=cartes)


@membre_panier.route('/membre/panier/add', methods=['POST'])
@login_required
def add_panier():

    id_item = request.form.get('id_item')

    # Sert à savoir si la demande vient du panier ou de la card individuelle de l'item
    from_panier = False

    # Quantité d'un item initialisée à 1 lorsque non trouvé (notamment dans le cas d'un ajout depuis le card de l'item)
    quantite_panier = int(request.form.get('quantite_panier', 1))


    # Récupération du type de l'item
    mycursor = get_db().cursor()
    sql = ''' SELECT type_item_id 
                      FROM Item 
                      WHERE id_item = %s; '''
    mycursor.execute(sql, (id_item))
    id_type_item = mycursor.fetchone()['type_item_id']


    # Si id_sexe n'est pas trouvé alors cela veut dire que le membre ajoute cet item depuis sa card individuelle et non le panier
    if request.form.get('id_sexe'):
        id_sexe = request.form.get('id_sexe')
        from_panier = True

    # Dans le cas où l'item est une Espece, on met son sexe par défaut à aléatoire (id_sexe = 3)
    elif id_type_item == 1:
        id_sexe = 3

    # Sinon cela veut dire que l'item n'est pas une Espece et n'a donc pas de sexe (id_sexe = 4)
    else:
        id_sexe = 4


    sql = ''' SELECT item_id,
                     sexe_id,
                     quantite_panier
              FROM Ligne_Panier
              
              WHERE item_id = %s 
              AND membre_id = %s
              AND sexe_id = %s; '''
    mycursor.execute(sql, (id_item, session['id_membre'], id_sexe))
    item_panier = mycursor.fetchone()

    if item_panier:
        sql = ''' UPDATE Ligne_Panier 
                  SET quantite_panier = %s
                   
                  WHERE item_id = %s 
                  AND membre_id = %s 
                  AND sexe_id = %s; '''
        mycursor.execute(sql, (quantite_panier, id_item, session['id_membre'], id_sexe))
        get_db().commit()

        # Si la demande d'ajout d'item vient du panier,  on rafraichit la partie nécessaire via la fonction ci-dessus
        if from_panier:
            return refresh_panier()
        # Sinon on redirige vers le panier car il faut refresh la page entière et pas seulement le panier
        else:
            return redirect('/membre/panier')

    else:
        # Ajout d'un sexe défini si l'item est une Espece
        if id_type_item == 1:
            id_sexe = 3

        sql = ''' INSERT INTO Ligne_Panier(item_id, membre_id, sexe_id, quantite_panier) VALUES (%s, %s, %s, %s); '''
        mycursor.execute(sql, (id_item, session['id_membre'], id_sexe, quantite_panier))

        get_db().commit()
        return redirect('/membre/panier')


@membre_panier.route('/membre/panier/delete', methods=['POST'])
@login_required
def delete_panier():
    id_item = request.form['id_item']
    id_sexe = request.form.get('id_sexe')

    mycursor = get_db().cursor()

    sql = ''' DELETE FROM Ligne_Panier WHERE membre_id = %s AND item_id = %s AND sexe_id = %s; '''
    mycursor.execute(sql, (session['id_membre'], id_item, id_sexe))
    get_db().commit()

    flash('Article supprimé', 'success')
    return redirect('/membre/panier')


@membre_panier.route('/membre/panier/delete/all', methods=['POST'])
@login_required
def delete_all_panier():
    mycursor = get_db().cursor()

    sql = ''' DELETE FROM Ligne_Panier WHERE membre_id = %s; '''
    mycursor.execute(sql, (session['id_membre'],))
    get_db().commit()

    flash('Panier vidé avec succès', 'success')
    return redirect('/membre/panier')


@membre_panier.route('/membre/panier/sexe', methods=['POST'])
@login_required
def change_sexe_article():
    id_item = request.form.get('id_item')
    id_sexe = int(request.form.get('id_sexe'))
    quantite_panier = int(request.form.get('quantite_panier'))

    mycursor = get_db().cursor()

    # Valeure maximale du sexe
    if id_sexe == 3:
        nv_sexe = 1
    else:
        nv_sexe = id_sexe + 1


    if quantite_panier > 1:
        sql = ''' UPDATE Ligne_Panier SET quantite_panier = quantite_panier - 1 WHERE item_id = %s AND membre_id = %s AND sexe_id = %s; '''
        mycursor.execute(sql, (id_item, session['id_membre'], id_sexe))
    else:
        sql = ''' DELETE FROM Ligne_Panier WHERE item_id = %s AND membre_id = %s AND sexe_id = %s; '''
        mycursor.execute(sql, (id_item, session['id_membre'], id_sexe))


    sql = ''' SELECT membre_id,
                     item_id,
                     sexe_id,
                     quantite_panier
              FROM Ligne_Panier 
              WHERE membre_id = %s 
              AND item_id = %s 
              AND sexe_id = %s; '''
    mycursor.execute(sql, (session['id_membre'], id_item, nv_sexe))
    article = mycursor.fetchone()

    if article:
        sql = ''' UPDATE Ligne_Panier SET quantite_panier = quantite_panier + 1 WHERE membre_id = %s AND item_id = %s AND sexe_id = %s; '''
        mycursor.execute(sql, (session['id_membre'], id_item, nv_sexe))
    else:
        sql = ''' INSERT INTO Ligne_Panier(membre_id, item_id, quantite_panier, sexe_id) VALUES (%s, %s, %s, %s); '''
        mycursor.execute(sql, (session['id_membre'], id_item, 1, nv_sexe))

    get_db().commit()
    return refresh_panier()