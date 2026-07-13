from controllers.auth import *
from controllers.membre import *
from controllers.membre_commandes import *
from controllers.admin import *
from controllers.admin_invocations import *
from controllers.membre_panier import *
from controllers.membre_reventes import *
from controllers.admin_commandes import *
from controllers.admin_reventes import *
from controllers.admin_settings import *
from controllers.admin_cartes import *

from controllers.items import *


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = 'SECRET_KEY'


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.route("/")
def home():
    mycursor = get_db().cursor()

    sql = ''' SELECT id_membre,
                     nom_membre,
                     gold,
                     RANK() OVER (ORDER BY gold DESC) AS Place
              FROM Membre
              WHERE role_id != 4 AND role_id != 5
              ORDER BY gold DESC; '''
    mycursor.execute(sql)
    membres = mycursor.fetchall()


    final_membres = []
    actual_id_membre = session.get('id_membre')
    flag = True
    membre_trouve = True if actual_id_membre is None else False

    index = 0
    while flag and (index<len(membres)):
        if (actual_id_membre == membres[index]['id_membre']):
            membre_trouve = True

        if ((index > 8) and (membre_trouve)):
            flag = False

        if (index <= 9) or (membre_trouve):
            final_membres.append(membres[index])

        index += 1


    return render_template("layout.html", membres=final_membres, actual_id_membre=actual_id_membre)


# @app.route("/TEST")
# def test():
#     requests.post(
#         "http://127.0.0.1:9814/send-dm",
#         json={
#             "discordId": 341190382081671169,
#             "message": "Ceci est un test"
#         },
#         headers={"Authorization": "SECRET_KEY"}
#     )
#     return "Envoyé"


@app.route("/boutique")
def boutique():
    mycursor = get_db().cursor()

    sql = ''' SELECT id_type_item, 
                     nom_type_item 
              FROM Type_Item 
              WHERE purchasable
              ORDER BY nom_type_item; '''
    mycursor.execute(sql)
    types = mycursor.fetchall()

    for type in types:

        sql = f''' SELECT id_item,
                          nom_item,
                          image_item
                   FROM Item 
                   WHERE type_item_id = %s 
                   ORDER BY RAND(); '''
        mycursor.execute(sql, (type['id_type_item'],))
        item = mycursor.fetchone()

        if item:
            type['nom_item'] = item['nom_item']
            type['image_item'] = item['image_item']

    return render_template("boutique/boutique.html", types=types)


@app.route("/conditions_generales_utilisation")
def conditions_generales_utilisation():
    return render_template("legal/conditions_generales_utilisation.html")

@app.route("/mentions_legales")
def mentions_legales():
    return render_template("legal/mentions_legales.html")

@app.route("/politique_de_confidentialité")
def politique_de_confidentialité():
    return render_template("legal/politique_de_confidentialité.html")

@app.route("/contact")
def contact():
    return render_template("legal/contact.html")

@app.route("/suppression_compte")
def suppression_compte():
    return render_template("legal/suppression_compte.html")


app.register_blueprint(auth)
app.register_blueprint(membre)
app.register_blueprint(membre_panier)
app.register_blueprint(membre_commandes)
app.register_blueprint(membre_reventes)
app.register_blueprint(admin)
app.register_blueprint(invocations)
app.register_blueprint(admin_commandes)
app.register_blueprint(admin_reventes)
app.register_blueprint(admin_settings)
app.register_blueprint(admin_cartes)
app.register_blueprint(items)

if __name__ == '__main__':
    app.run()
