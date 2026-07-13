from flask import Flask, request, render_template, redirect, flash, session, g, Blueprint
import os
from werkzeug.utils import secure_filename
from connexion_db import get_db
from decorators import admin_required, editor_required, login_required
from function import get_admin_cmd
from queries import queries

items = Blueprint('items', __name__, template_folder='templates')

UPLOAD_ITEMS_IMAGES = 'static/images/boutique'

def get_especes_cartes(item: dict) -> None:

    if item.get('Variantes'):

        mycursor = get_db().cursor()

        sql = ''' SELECT Carte.id_carte,
                         Carte.nom_carte
                   
                  FROM Carte
                  JOIN Apparition ON Apparition.carte_id = Carte.id_carte
                
                  WHERE Apparition.espece_id = %s
                  AND Apparition.variante_id = %s; '''

        for variante in item['Variantes']:
            mycursor.execute(sql, (item['Main']['id_item'], variante['id_variante']))
            variante['Cartes'] = mycursor.fetchall()


@items.route('/boutique/items/show', methods=['GET'])
def items_show():

    id_type_item = request.args.get('id_type_item')

    mycursor = get_db().cursor()

    sql = ''' SELECT id_type_item, 
                     nom_type_item 
              FROM Type_Item 
              WHERE purchasable AND id_type_item = %s
              ORDER BY nom_type_item; '''
    mycursor.execute(sql, (id_type_item,))
    type = mycursor.fetchone()

    # Récupération de la requête en fonction de la catégorie
    sql = queries['show'][id_type_item]['Main']['Query']
    mycursor.execute(sql)
    items = mycursor.fetchall()

    return render_template('boutique/items/show/show_items.html', type=type, items=items)


@items.route('/boutique/items/search')
def search_items():

    id_type_item = request.args.get('id_type_item')
    search_item = request.args.get('search_item')

    mycursor = get_db().cursor()

    sql = ''' SELECT id_type_item, 
                     nom_type_item 
              FROM Type_Item 
              WHERE purchasable AND id_type_item = %s
              ORDER BY nom_type_item; '''
    mycursor.execute(sql, (id_type_item,))
    type = mycursor.fetchone()

    sql = queries['search'][id_type_item]['Main']['Query']
    mycursor.execute(sql, (f"%{search_item}%",))
    items = mycursor.fetchall()

    return render_template("boutique/items/show/_show_items.html", type=type, items=items)


@items.route('/boutique/items/card', methods=['GET'])
def card_items():

    id_type_item = request.args.get('id_type_item')
    id_item = request.args.get('id_item')

    mycursor = get_db().cursor()

    sql = ''' SELECT id_type_item, 
                     nom_type_item 
              FROM Type_Item 
              WHERE purchasable AND id_type_item = %s
              ORDER BY nom_type_item; '''
    mycursor.execute(sql, (id_type_item,))
    type = mycursor.fetchone()

    ctx = {'id_item': id_item}
    item = {}

    for query, entry in queries['card'][id_type_item].items():
        params = tuple(ctx[val] for val in entry['Params'])
        mycursor.execute(entry['Query'], params)

        if entry['Many']:
            data = mycursor.fetchall()
        else:
            data = mycursor.fetchone()
            if data:
                for key, val in data.items():
                    if key not in ctx:
                        ctx[key] = val

        item[query] = data

    # Ajout des cartes d'apparition dans 'item['Variantes']' dans le cas d'une espèce
    get_especes_cartes(item)

    # Remplacement de la 'commande_admin_item' par sa version complète
    item['Main']['commande_admin_item'] = get_admin_cmd(item['Main'])

    return render_template('boutique/items/card/card_items.html', type=type, item=item)


@items.route('/boutique/items/delete', methods=['GET'])
@admin_required
def delete_items():

    id_item = request.args.get('id_item')

    mycursor = get_db().cursor()
    sql = ''' DELETE FROM Item WHERE id_item = %s; '''
    mycursor.execute(sql, (id_item,))

    get_db().commit()

    flash(f'Item {id_item} supprimé !')
    return redirect('/boutique')


@items.route('/boutique/items/add', methods=['GET'])
@admin_required
def add_items():

    id_type_item = request.args.get('id_type_item')
    mycursor = get_db().cursor()

    sql = ''' SELECT id_type_item, 
                     nom_type_item 
              FROM Type_Item 
              WHERE purchasable AND id_type_item = %s
              ORDER BY nom_type_item; '''
    mycursor.execute(sql, (id_type_item,))
    type = mycursor.fetchone()

    ctx = {}
    item = {}

    for (query, entry) in queries['add_get'][id_type_item].items():
        params = tuple(ctx[val] for val in entry['Params'])
        mycursor.execute(entry['Query'], params)

        if entry['Many']:
            data = mycursor.fetchall()

        else:
            data = mycursor.fetchone()
            if data:
                for key, val in data.items():
                    if key not in ctx:
                        ctx[key] = val

        item[query] = data

    return render_template('boutique/items/add/add_items.html', type=type, item=item)


@items.route('/boutique/items/add', methods=['POST'])
@admin_required
def valid_add_items():
    ctx = {}

    # Boucle permettant de remplir le dico 'ctx' en tenant compte des champs possédant plusieurs valeurs
    for key in request.form:
        if key.endswith('[]'):
            # Cas exceptionnel : "apparitions_<id_variante>[]" -> liste des id_carte pour cette variante
            if 'apparitions' in key:
                id_variante = key[-3]

                # ctx['variantes_ids'] existe normalement déjà car les éléments du formulaire sont envoyés dans un ordre précis
                ctx['variantes_ids'][id_variante] = request.form.getlist(key)

            else:
                clean_key = key[:-2]
                ctx[clean_key] = {}
                values = request.form.getlist(key)

                for value in values:
                    ctx[clean_key][value] = {}

        else:
            ctx[key] = request.form.get(key)


    # Etapes d'insertions de l'item dans la BDD en fonction du type (si un item n'a pas de cas, c'est qu'il n'a pas de caractéristiques spéciales à ajouter pour l'instant)
    id_type_item = ctx['id_type_item']
    mycursor = get_db().cursor()

    # Récupération du nom du type
    sql = ''' SELECT nom_type_item FROM Type_Item WHERE id_type_item = %s; '''
    mycursor.execute(sql, id_type_item)
    nom_type_item = mycursor.fetchone()['nom_type_item']

    # Ajout de l'image aux fichiers
    file = request.files.get('image_item')
    image_item = None
    if file:
        dir = f"{UPLOAD_ITEMS_IMAGES}/{nom_type_item}/"
        image_item = secure_filename(f"{ctx['nom_item']}.png")
        file.save(os.path.join(dir, image_item))


    # Requête commune à tous les types pour ajouter les infos de base de l'item
    sql = ''' INSERT INTO Item(nom_item, prix_item, commande_admin_item, type_item_id, image_item) VALUES (%s, %s, %s, %s, %s); '''
    insert = (ctx['nom_item'], ctx['prix_item'], ctx['commande_admin_item'], id_type_item, image_item)
    mycursor.execute(sql, insert)

    # récupération de l'id du nouvel item
    id_item = mycursor.lastrowid

    # ----- Cas Espece -------
    if id_type_item == '1':

        # Ajout des caractèristique d'une espece
        sql = ''' INSERT INTO Espece(id_item, taming, oeuf_id, biome_id, nourriture_id) VALUES (%s, %s, %s, %s, %s); '''
        insert = (id_item, ctx['taming'], ctx['id_oeuf'], ctx['id_biome'], ctx['id_nourriture'])
        mycursor.execute(sql, insert)

        if ctx.get('trophes_ids'):
            # Ajout de tous les trophés que l'espece peut donner
            for id_trophe in ctx['trophes_ids']:
                sql = ''' INSERT INTO Espece_Trophe(espece_id, trophe_id) VALUES (%s, %s); '''
                insert = (id_item, id_trophe)
                mycursor.execute(sql, insert)

        # Ajout de toutes les apparitions de l'espece sous toutes les variantes et toutes les cartes données dans 'ctx['variantes_id']'
        if ctx.get('variantes_ids'):
            for id_variante in ctx['variantes_ids']:
                for id_carte in ctx['variantes_ids'][id_variante]:
                    sql = ''' INSERT INTO Apparition(espece_id, variante_id, carte_id) VALUES (%s, %s, %s); '''
                    insert = (id_item, id_variante, id_carte)
                    mycursor.execute(sql, insert)


    # ----- Cas Nourriture -------
    if id_type_item == '2':
        # Ajout de l'item dans la table Nourriture avec ses caractéristiques (aucune carac dans cette version)
        sql = ''' INSERT INTO Nourriture(id_item) VALUES (%s); '''
        insert = (id_item)
        mycursor.execute(sql, insert)


    # ----- Cas Arme -------
    if id_type_item == '3':
        # Ajout de l'item dans la table Arme avec ses caractéristiques (aucune carac dans cette version)
        sql = ''' INSERT INTO Arme(id_item) VALUES (%s); '''
        insert = (id_item)
        mycursor.execute(sql, insert)

        if ctx.get('munitions_id'):
            # Ajout de toutes les munitions associées à l'arme
            for id_munition in ctx['munitions_id']:
                sql = ''' INSERT INTO Arme_Munition(arme_id, munition_id) VALUES (%s, %s); '''
                insert = (id_item, id_munition)
                mycursor.execute(sql, insert)


    # ----- Cas Munition -------
    if id_type_item == '4':
        # Ajout de l'item dans la table concernée avec ses caractéristiques (aucune carac dans cette version)
        sql = ''' INSERT INTO Munition(id_item) VALUES (%s); '''
        insert = (id_item)
        mycursor.execute(sql, insert)


    # ----- Cas Structure -------
    if id_type_item == '5':
        # Ajout de l'item dans la table concernée avec ses caractéristiques (aucune carac dans cette version)
        sql = ''' INSERT INTO Structure(id_item) VALUES (%s); '''
        insert = (id_item)
        mycursor.execute(sql, insert)


    # ----- Cas Objet -------
    if id_type_item == '6':
        # Ajout de l'item dans la table concernée avec ses caractéristiques (aucune carac dans cette version)
        sql = ''' INSERT INTO Objet(id_item) VALUES (%s); '''
        insert = (id_item)
        mycursor.execute(sql, insert)


    # ----- Cas Trophé -------
    if id_type_item == '7':
        # Ajout de l'item dans la table concernée avec ses caractéristiques (aucune carac dans cette version)
        sql = ''' INSERT INTO Trophe(id_item) VALUES (%s); '''
        insert = (id_item)
        mycursor.execute(sql, insert)


    get_db().commit()
    flash('Item ajouté avec succès !')
    return redirect(f"/boutique/items/card?id_item={id_item}&id_type_item={id_type_item}")


@items.route('/boutique/items/edit', methods=['GET'])
def edit_items():

    id_item = request.args['id_item']
    id_type_item = request.args['id_type_item']

    mycursor = get_db().cursor()

    sql = ''' SELECT id_type_item, 
                         nom_type_item 
                  FROM Type_Item 
                  WHERE purchasable AND id_type_item = %s
                  ORDER BY nom_type_item; '''
    mycursor.execute(sql, (id_type_item,))
    type = mycursor.fetchone()


    # Récupération des informations actuelles de l'item concerné
    ctx = {'id_item': id_item}
    item = {}

    for query, entry in queries['card'][id_type_item].items():
        params = tuple(ctx[val] for val in entry['Params'])
        mycursor.execute(entry['Query'], params)

        if entry['Many']:
            data = mycursor.fetchall()
        else:
            data = mycursor.fetchone()
            if data:
                for key, val in data.items():
                    if key not in ctx:
                        ctx[key] = val

        item[query] = data


    # Récupération de tous les champs à sélectionner dans le formulaire en fonction de l'item (nourriture pref, etc)
    ctx = {}
    form = {}

    for (query, entry) in queries['add_get'][id_type_item].items():
        params = tuple(ctx[val] for val in entry['Params'])
        mycursor.execute(entry['Query'], params)

        if entry['Many']:
            data = mycursor.fetchall()

        else:
            data = mycursor.fetchone()
            if data:
                for key, val in data.items():
                    if key not in ctx:
                        ctx[key] = val

        form[query] = data

    return render_template('boutique/items/edit/edit_items.html', type=type, item=item, form=form)


@items.route('/boutique/items/edit', methods=['POST'])
def valid_edit_items():

    id_item = request.form['id_item']
    ctx = {}

    # Boucle permettant de remplir le dico 'ctx' en tenant compte des champs possédant plusieurs valeurs
    for key in request.form:
        if key.endswith('[]'):
            # Cas exceptionnel : "apparitions_<id_variante>[]" -> liste des id_carte pour cette variante
            if 'apparitions' in key:
                id_variante = key[-3]

                # ctx['variantes_ids'] existe normalement déjà car les éléments du formulaire sont envoyés dans un ordre précis
                ctx['variantes_ids'][id_variante] = request.form.getlist(key)

            else:
                clean_key = key[:-2]
                ctx[clean_key] = {}
                values = request.form.getlist(key)

                for value in values:
                    ctx[clean_key][value] = {}

        else:
            ctx[key] = request.form.get(key)

    # Etapes d'insertions de l'item dans la BDD en fonction du type (si un item n'a pas de cas, c'est qu'il n'a pas de caractéristiques spéciales à ajouter pour l'instant)
    id_type_item = ctx['id_type_item']
    mycursor = get_db().cursor()

    # Récupération du nom du type pour connaître dans quel répertoire ajouter l'image
    sql = ''' SELECT nom_type_item 
              FROM Type_Item 
              WHERE id_type_item = %s; '''
    mycursor.execute(sql, id_type_item)
    nom_type_item = mycursor.fetchone()['nom_type_item']


    # Ajout de l'image aux fichiers si le champ en contient une nouvelle
    file = request.files.get('image_item')
    if file:
        dir = f"{UPLOAD_ITEMS_IMAGES}/{nom_type_item}/"
        image_item = secure_filename(f"{ctx['nom_item']}.png")
        file.save(os.path.join(dir, image_item))

        # Requête commune à tous les types pour modifier les infos de base de l'item
        sql = ''' UPDATE Item SET nom_item = %s, prix_item = %s, commande_admin_item = %s, image_item = %s WHERE id_item = %s; '''
        insert = (ctx['nom_item'], ctx['prix_item'], ctx['commande_admin_item'], image_item, id_item)
        mycursor.execute(sql, insert)

    else:
        # Requête commune à tous les types pour modifier les infos de base de l'item
        sql = ''' UPDATE Item SET nom_item = %s, prix_item = %s, commande_admin_item = %s WHERE id_item = %s; '''
        insert = (ctx['nom_item'], ctx['prix_item'], ctx['commande_admin_item'], id_item)
        mycursor.execute(sql, insert)


    # ----- Cas Espece -------
    if id_type_item == '1':

        # Modification des caractèristique d'une espece
        sql = ''' UPDATE Espece SET id_item=%s, taming=%s, oeuf_id=%s, biome_id=%s, nourriture_id=%s WHERE id_item = %s; '''
        insert = (id_item, ctx['taming'], ctx['id_oeuf'], ctx['id_biome'], ctx['id_nourriture'], id_item)
        mycursor.execute(sql, insert)

        if ctx.get('trophe_ids'):
            # Modification de tous les trophés que l'espece peut donner
            sql = ''' DELETE FROM Espece_Trophe WHERE espece_id = %s; '''
            mycursor.execute(sql, id_item)
            for id_trophe in ctx['trophes_ids']:
                sql = ''' INSERT INTO Espece_Trophe(espece_id, trophe_id) VALUES (%s, %s); '''
                insert = (id_item, id_trophe)
                mycursor.execute(sql, insert)

        if ctx.get('variantes_ids'):
            # Modification de toutes les apparitions de l'espece sous toutes les variantes et toutes les cartes données dans 'ctx['variantes_id']'
            sql = ''' DELETE FROM Apparition WHERE espece_id = %s; '''
            mycursor.execute(sql, id_item)
            for id_variante in ctx['variantes_ids']:
                for id_carte in ctx['variantes_ids'][id_variante]:
                    sql = ''' INSERT INTO Apparition(espece_id, variante_id, carte_id) VALUES (%s, %s, %s); '''
                    insert = (id_item, id_variante, id_carte)
                    mycursor.execute(sql, insert)


    # ----- Cas Nourriture -------
    if id_type_item == '2':
        # Ajout de l'item dans la table Nourriture avec ses caractéristiques (aucune carac dans cette version)
        pass

    # ----- Cas Arme -------
    if id_type_item == '3':
        if ctx.get('munitions_id'):
            # Modification de toutes les munitions associées à l'arme
            sql = ''' DELETE FROM Arme_Munition WHERE arme_id = %s; '''
            mycursor.execute(sql, id_item)
            for id_munition in ctx['munitions_id']:
                sql = ''' INSERT INTO Arme_Munition(arme_id, munition_id) VALUES (%s, %s); '''
                insert = (id_item, id_munition)
                mycursor.execute(sql, insert)

    # ----- Cas Munition -------
    if id_type_item == '4':
        # Modification de l'item dans la table concernée avec ses caractéristiques (aucune carac dans cette version)
        pass

    # ----- Cas Structure -------
    if id_type_item == '5':
        # Modification de l'item dans la table concernée avec ses caractéristiques (aucune carac dans cette version)
        pass

    # ----- Cas Objet -------
    if id_type_item == '6':
        # Modification de l'item dans la table concernée avec ses caractéristiques (aucune carac dans cette version)
        pass

    # ----- Cas Trophé -------
    if id_type_item == '7':
        # Modification de l'item dans la table concernée avec ses caractéristiques (aucune carac dans cette version)
        pass

    get_db().commit()
    flash('Item modifié avec succès !')
    return redirect(f"/boutique/items/card?id_item={id_item}&id_type_item={id_type_item}")