from datetime import datetime, timedelta
from connexion_db import get_db


def auto_add_item_copy(ligne: dict) -> int:
    ''' Prend en paramètre les caractéristiques d'un item (nom, prix, type et commande_admin)
        Si une copie existe déjà dans la table 'Item_Copy' alors la fonction renvoie l'id de cet item
        Si ce n'est pas le cas alors une copie est créée et son id est renvoyé '''

    mycursor = get_db().cursor()

    sql = ''' SELECT id_item_copy
              FROM Item_Copy 

              WHERE nom_item_copy = %s
              AND prix_item_copy = %s
              AND type_item_id = %s
              AND commande_admin_item_copy = %s; '''
    insert = (ligne['nom_item'], ligne['prix_item'], ligne['type_item_id'], ligne['commande_admin_item'])
    mycursor.execute(sql, insert)
    id_item_copy = mycursor.fetchone()

    if not id_item_copy:
        sql = ''' INSERT INTO Item_Copy(nom_item_copy, prix_item_copy, commande_admin_item_copy, type_item_id, image_item_copy) VALUES (%s, %s, %s, %s, %s); '''
        insert = (ligne['nom_item'], ligne['prix_item'], ligne['commande_admin_item'], ligne['type_item_id'], ligne['image_item'])
        mycursor.execute(sql, insert)

        id_item_copy = mycursor.lastrowid

    else:
        id_item_copy = id_item_copy.get('id_item_copy')

    return id_item_copy


def get_admin_cmd(item: dict, quantite: int = 1) -> str:
    ''' Permet de générer la commande complète de spawn d'un item en fonction de son type '''

    mycursor = get_db().cursor()
    sql = "SELECT niv_max_dino FROM CONFIG;"
    mycursor.execute(sql)

    niv_max = mycursor.fetchone()["niv_max_dino"]
    niv_max = niv_max + (niv_max//2)

    if item.get('type_item_id') == 1:
        cmd = f"cheat SDF {item.get('commande_admin_item', item.get('commande_admin_item_copy'))} 1 {niv_max}"

    else:
        cmd = f"cheat GFI {item.get('commande_admin_item', item.get('commande_admin_item_copy'))} {quantite} 10 0"

    return cmd


def get_temps_restant(id_membre: int) -> str:
    mycursor = get_db().cursor()

    sql = """ SELECT date_revente FROM Revente WHERE membre_id = %s ORDER BY date_revente DESC; """
    mycursor.execute(sql, (id_membre,))
    date_revente = mycursor.fetchone()['date_revente']

    sql = """ SELECT interval_revente FROM CONFIG; """
    mycursor.execute(sql)
    interval_revente = mycursor.fetchone()["interval_revente"]

    interval_revente = timedelta(days=interval_revente)

    now = datetime.now()
    fin = date_revente + interval_revente
    temps_restant = fin - now

    total_seconds = int(temps_restant.total_seconds())
    heures = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    return f"[{heures:02d} heures {minutes:02d} min]"


def get_plafond_revente(id_membre: int) -> int:
    ''' Récupère le plafond restant avec reset complet après que l'interval défini soit passé '''

    mycursor = get_db().cursor()

    sql = ''' SELECT montant_revente,
                     interval_revente
              FROM CONFIG; '''
    mycursor.execute(sql)
    config = mycursor.fetchone()

    interval_revente = config["interval_revente"]
    montant_revente = config["montant_revente"]

    sql = """
        SELECT date_revente
        FROM Revente
        WHERE membre_id = %s AND TIMESTAMPDIFF(DAY, date_revente, NOW()) <= %s
        ORDER BY date_revente ASC; """
    mycursor.execute(sql, (id_membre, interval_revente))
    last = mycursor.fetchone()

    if not last:
        reponse = montant_revente

    else:
        cycle_start = last["date_revente"]

        sql = """
            SELECT SUM(Item_Copy.prix_item_copy * Ligne_Revente.quantite_revente) AS prix_revente
            
            FROM Revente
            JOIN Ligne_Revente ON Ligne_Revente.revente_id = Revente.id_revente
            JOIN Item_Copy ON Item_Copy.id_item_copy = Ligne_Revente.item_copy_id
            
            WHERE membre_id = %s 
            AND date_revente >= %s; """
        mycursor.execute(sql, (id_membre, cycle_start))
        reventes = mycursor.fetchone()

        total = reventes['prix_revente'] or 0
        reponse = montant_revente - total

    return reponse