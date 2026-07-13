from flask import Flask, request, render_template, redirect, flash, session, g, Blueprint
from connexion_db import get_db
from decorators import *
from function import *

admin_settings = Blueprint('admin_settings', __name__, template_folder='templates')


@admin_settings.route('/admin/settings', methods=['GET'])
@admin_required
def show_settings():
    mycursor = get_db().cursor()

    sql = ''' SELECT montant_revente AS 'Montant de revente (gold)',
                     interval_revente AS 'Intervalle de revente (jours)',
                     niv_max_dino AS 'Niveau max dino',
                     gain_giveaway AS 'Gain Giveaway',
                     gold_depart AS 'Gold départ',
                     gain_journalier AS 'Gain Journalier'
              FROM CONFIG; '''
    mycursor.execute(sql)
    settings = mycursor.fetchone()

    return render_template('admin/settings/show_settings.html', settings=settings)


@admin_settings.route('/admin/settings/edit', methods=['GET'])
@admin_required
def edit_settings():
    mycursor = get_db().cursor()

    sql = ''' SELECT montant_revente,
                     interval_revente,
                     niv_max_dino,
                     gain_giveaway,
                     gold_depart,
                     gain_journalier
              FROM CONFIG; '''
    mycursor.execute(sql)
    settings = mycursor.fetchone()

    return render_template('/admin/settings/edit_settings.html', settings=settings)


@admin_settings.route('/admin/settings/edit', methods=['POST'])
@admin_required
def valid_edit_settings():

    settings = dict(request.form)
    mycursor = get_db().cursor()

    for setting in settings:
        sql = f''' UPDATE CONFIG SET {setting} = {settings[setting]} WHERE 1;'''
        mycursor.execute(sql)

    get_db().commit()
    flash('Modification validées')
    return redirect('/admin/settings')