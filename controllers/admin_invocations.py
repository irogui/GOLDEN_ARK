from flask import Flask, request, render_template, redirect, flash, session, g, Blueprint
from connexion_db import get_db
from decorators import *

invocations = Blueprint('invocations', __name__, template_folder='templates')


@invocations.route('/admin/invocation')
@admin_required
def show_invocation():

    mycursor = get_db().cursor()

    sql = ''' SELECT id_invocation,
                     nom_invocation,
                     nom_carte,
                     nom_espece,
                     nb_invocation,
                     niveau_invocation,
                     hm_invocation,
                     intervalle
                     
                     FROM Invocation
                     JOIN Espece ON Espece.id_espece = Invocation.espece_id
                     JOIN Carte ON Carte.id_carte = Invocation.carte_id
                     
                     ORDER BY id_invocation DESC;
                     '''

    mycursor.execute(sql)
    invocations = mycursor.fetchall()

    return render_template('/admin/invocations/show_invocations.html', invocations=invocations)


@invocations.route('/admin/invocation/add', methods=['GET'])
@admin_required
def add_invocation():

    mycursor = get_db().cursor()

    sql = ''' SELECT * FROM Carte WHERE dispo_carte; '''
    mycursor.execute(sql)
    cartes = mycursor.fetchall()

    sql = ''' SELECT * FROM Espece ORDER BY nom_espece; '''
    mycursor.execute(sql)
    especes = mycursor.fetchall()

    return render_template('/admin/invocations/add_invocations.html', cartes=cartes, especes=especes)


@invocations.route('/admin/invocation/add', methods=['POST'])
@admin_required
def valid_add_invocation():

    nom_invocation = request.form.get('nom_invocation')
    id_carte = request.form.get('id_carte')
    id_espece = request.form.get('id_espece')
    niveau_invocation = request.form.get('niveau_invocation')
    nb_invocation = request.form.get('nb_invocation')
    hm_invocation = request.form.get('hm_invocation')
    intervalle = request.form.get('intervalle')
    message_invocation = request.form.get('message_invocation')
    show_invocation = request.form.get('show_invocation')
    coo_invocation_x = request.form.get('coo_invocation_x')
    coo_invocation_y = request.form.get('coo_invocation_y')

    if show_invocation == 'on':
        show_invocation = True
    else:
        show_invocation = False

    mycursor = get_db().cursor()
    insert = (nom_invocation, message_invocation, show_invocation, hm_invocation, intervalle, nb_invocation, niveau_invocation, coo_invocation_x, coo_invocation_y, id_espece, id_carte)

    sql = ''' INSERT INTO Invocation(nom_invocation,
                                    message_invocation,
                                    show_invocation,
                                    hm_invocation,
                                    intervalle,
                                    nb_invocation,
                                    niveau_invocation,
                                    coo_invocation_x,
                                    coo_invocation_y,
                                    espece_id,
                                    carte_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'''
    mycursor.execute(sql, insert)
    get_db().commit()

    return redirect('/admin/invocation')


@invocations.route('/admin/invocation/edit', methods=['GET'])
@admin_required
def edit_invocation():
    id_invocation = request.args.get('id_invocation')

    mycursor = get_db().cursor()

    sql = ''' SELECT * FROM Invocation WHERE id_invocation = %s; '''
    mycursor.execute(sql, (id_invocation,))
    invocation = mycursor.fetchone()

    sql = ''' SELECT * FROM Carte WHERE dispo_carte; '''
    mycursor.execute(sql)
    cartes = mycursor.fetchall()

    sql = ''' SELECT * FROM Espece ORDER BY nom_espece; '''
    mycursor.execute(sql)
    especes = mycursor.fetchall()

    return render_template('admin/invocations/edit_invocations.html', cartes=cartes, especes=especes, invocation=invocation)


@invocations.route('/admin/invocation/edit', methods=['POST'])
@admin_required
def valid_edit_invocation():
    id_invocation = request.form.get('id_invocation')
    nom_invocation = request.form.get('nom_invocation')
    id_carte = request.form.get('id_carte')
    id_espece = request.form.get('id_espece')
    niveau_invocation = request.form.get('niveau_invocation')
    nb_invocation = request.form.get('nb_invocation')
    hm_invocation = request.form.get('hm_invocation')
    intervalle = request.form.get('intervalle')
    message_invocation = request.form.get('message_invocation')
    show_invocation = request.form.get('show_invocation')
    coo_invocation_x = request.form.get('coo_invocation_x')
    coo_invocation_y = request.form.get('coo_invocation_y')

    if show_invocation == 'on':
        show_invocation = True
    else:
        show_invocation = False

    mycursor = get_db().cursor()
    insert = (nom_invocation, message_invocation, show_invocation, hm_invocation, intervalle, nb_invocation, niveau_invocation, coo_invocation_x, coo_invocation_y, id_espece, id_carte, id_invocation)

    sql = ''' UPDATE Invocation SET 
                    nom_invocation=%s, message_invocation=%s, show_invocation=%s, hm_invocation=%s, intervalle=%s, nb_invocation=%s, niveau_invocation=%s, coo_invocation_x=%s, coo_invocation_y=%s, espece_id=%s, carte_id=%s
                    WHERE id_invocation = %s; '''
    mycursor.execute(sql, insert)

    get_db().commit()

    return redirect('/admin/invocation')


@invocations.route('/admin/invocation/delete', methods=['GET'])
@admin_required
def delete_invocations():

    id_invocation = request.args.get('id_invocation')

    mycursor = get_db().cursor()

    sql = ''' DELETE FROM Invocation WHERE id_invocation = %s; '''
    mycursor.execute(sql, (id_invocation,))
    get_db().commit()

    return redirect('/admin/invocation')