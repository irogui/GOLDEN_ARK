from flask import Flask, request, render_template, redirect, flash, session, g, Blueprint
from connexion_db import get_db
from decorators import *
from function import *

admin_cartes = Blueprint('admin_cartes', __name__, template_folder='templates')

@admin_cartes.route('/admin/cartes', methods=['GET'])
@admin_required
def show_cartes():

    mycursor = get_db().cursor()

    sql = ''' SELECT id_carte,
                     nom_carte,
                     dispo_carte,
                     coo_boutique
               FROM Carte 
               WHERE id_carte <= 12
               ORDER BY dispo_carte DESC, id_carte; '''
    mycursor.execute(sql)
    cartes = mycursor.fetchall()

    return render_template('admin/cartes/show_cartes.html', cartes=cartes)


@admin_cartes.route('/admin/cartes/edit', methods=['GET'])
@admin_required
def edit_cartes():

    id_carte = request.args.get('id_carte')

    if (id_carte is None) or (int(id_carte) > 12) or (int(id_carte) < 0):
        flash("L'identifiant de carte est incorrect")
        return redirect('/admin/cartes')

    else:
        mycursor = get_db().cursor()

        sql = ''' SELECT id_carte,
                         nom_carte,
                         dispo_carte,
                         coo_boutique
                   FROM Carte 
                   WHERE id_carte = %s '''
        mycursor.execute(sql, (id_carte,))
        carte = mycursor.fetchone()

        if carte.get('coo_boutique'):
            lat, lon = carte['coo_boutique'].split('/')
            carte['lat'] = lat
            carte['lon'] = lon

        return render_template('admin/cartes/carte_edit.html', carte=carte)


@admin_cartes.route('/admin/cartes/edit', methods=['POST'])
@admin_required
def valid_edit_cartes():

    id_carte = request.form.get('id_carte')

    if (id_carte is None) or (int(id_carte) > 12) or (int(id_carte) < 0):
        flash("L'identifiant de carte est incorrect, les modifications on échouées")


    else:
        mycursor = get_db().cursor()

        carte = dict(request.form)

        coo_boutique = None
        if carte.get('lat') and carte.get('lon'):
            coo_boutique = f"{carte.get('lat')}/{carte.get('lon')}"

        sql = ''' UPDATE Carte SET dispo_carte = %s, coo_boutique = %s WHERE id_carte = %s '''
        insert = (carte['dispo_carte'], coo_boutique, id_carte)
        mycursor.execute(sql, insert)

        get_db().commit()
        flash('Modification enregistrées')

    return redirect('/admin/cartes')