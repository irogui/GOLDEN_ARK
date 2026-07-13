queries = {

    # -------------------------------------------------------
    # Affichage catégorisé complet
    # -------------------------------------------------------

    'show': {

        '1': {
            'Main': {
                'Many': True,
                'Params': [],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id,
                           Espece.taming,
                           Biome.nom_biome

                    FROM Espece
                    JOIN Item ON Item.id_item = Espece.id_item
                    JOIN Biome ON Biome.id_biome = Espece.biome_id

                    ORDER BY Item.nom_item;
                '''
            }
        },

        '2': {
            'Main': {
                'Many': True,
                'Params': [],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Nourriture
                    JOIN Item ON Item.id_item = Nourriture.id_item

                    WHERE EXISTS (
                        SELECT 1
                        FROM Compose_Nourriture
                        WHERE Compose_Nourriture.plat_id = Nourriture.id_item
                    )

                    ORDER BY Item.nom_item;
                '''
            }
        },

        '3': {
            'Main': {
                'Many': True,
                'Params': [],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Arme
                    JOIN Item ON Item.id_item = Arme.id_item

                    ORDER BY Item.nom_item;
                '''
            }
        },

        '4': {
            'Main': {
                'Many': True,
                'Params': [],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Munition
                    JOIN Item ON Item.id_item = Munition.id_item

                    ORDER BY Item.nom_item;
                '''
            }
        },

        '5': {
            'Main': {
                'Many': True,
                'Params': [],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Structure
                    JOIN Item ON Item.id_item = Structure.id_item

                    ORDER BY Item.nom_item;
                '''
            }
        },

        '6': {
            'Main': {
                'Many': True,
                'Params': [],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Objet
                    JOIN Item ON Item.id_item = Objet.id_item

                    ORDER BY Item.nom_item;
                '''
            }
        },

        '7': {
            'Main': {
                'Many': True,
                'Params': [],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Trophe
                    JOIN Item ON Item.id_item = Trophe.id_item

                    ORDER BY Item.nom_item;
                '''
            }
        },
    },

    # -------------------------------------------------------
    # Filtre dynamique (search)
    # -------------------------------------------------------

    'search': {

        '1': {
            'Main': {
                'Many': True,
                'Params': ['search_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id,
                           Espece.taming,
                           Biome.nom_biome

                    FROM Espece
                    JOIN Item ON Item.id_item = Espece.id_item
                    JOIN Biome ON Biome.id_biome = Espece.biome_id

                    WHERE Item.nom_item LIKE %s

                    ORDER BY Item.nom_item;
                '''
            }
        },

        '2': {
            'Main': {
                'Many': True,
                'Params': ['search_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Nourriture
                    JOIN Item ON Item.id_item = Nourriture.id_item

                    WHERE Item.nom_item LIKE %s
                    AND EXISTS (
                        SELECT 1
                        FROM Compose_Nourriture
                        WHERE Compose_Nourriture.plat_id = Nourriture.id_item
                    )

                    ORDER BY Item.nom_item;
                '''
            }
        },

        '3': {
            'Main': {
                'Many': True,
                'Params': ['search_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Arme
                    JOIN Item ON Item.id_item = Arme.id_item

                    WHERE Item.nom_item LIKE %s

                    ORDER BY Item.nom_item;
                '''
            }
        },

        '4': {
            'Main': {
                'Many': True,
                'Params': ['search_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Munition
                    JOIN Item ON Item.id_item = Munition.id_item

                    WHERE Item.nom_item LIKE %s

                    ORDER BY Item.nom_item;
                '''
            }
        },

        '5': {
            'Main': {
                'Many': True,
                'Params': ['search_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Structure
                    JOIN Item ON Item.id_item = Structure.id_item

                    WHERE Item.nom_item LIKE %s

                    ORDER BY Item.nom_item;
                '''
            }
        },

        '6': {
            'Main': {
                'Many': True,
                'Params': ['search_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Objet
                    JOIN Item ON Item.id_item = Objet.id_item

                    WHERE Item.nom_item LIKE %s

                    ORDER BY Item.nom_item;
                '''
            }
        },

        '7': {
            'Main': {
                'Many': True,
                'Params': ['search_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Trophe
                    JOIN Item ON Item.id_item = Trophe.id_item

                    WHERE Item.nom_item LIKE %s

                    ORDER BY Item.nom_item;
                '''
            }
        },
    },

    # ─────────────────────────────────────────────
    # Fiche individuelle (card)
    # ─────────────────────────────────────────────

    'card': {

        '1': {
            'Main': {
                'Many': False,
                'Params': ['id_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id,
                           Espece.taming,
                           
                           Biome.id_biome,
                           Biome.nom_biome,
                           
                           Oeuf.id_oeuf,
                           Oeuf.taille_oeuf

                    FROM Espece
                    JOIN Item ON Item.id_item = Espece.id_item
                    JOIN Biome ON Biome.id_biome = Espece.biome_id
                    JOIN Oeuf ON Oeuf.id_oeuf = Espece.oeuf_id

                    WHERE Item.id_item = %s;
                '''
            },
            'Nourriture': {
                'Many': False,
                'Params': ['id_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id,
                           
                           EXISTS (
                           SELECT 1 
                           FROM Compose_Nourriture
                           WHERE Compose_Nourriture.plat_id = Item.id_item) AS est_plat

                    FROM Item
                    JOIN Nourriture ON Item.id_item = Nourriture.id_item
                    JOIN Espece ON Espece.nourriture_id = Item.id_item

                    WHERE Espece.id_item = %s;
                '''
            },
            'Trophes': {
                'Many': True,
                'Params': ['id_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Item
                    JOIN Trophe ON Trophe.id_item = Item.id_item
                    JOIN Espece_Trophe ON Espece_Trophe.Trophe_id = Trophe.id_item

                    WHERE Espece_Trophe.espece_id = %s;
                '''
            },

            'Variantes': {
                'Many': True,
                'Params': ['id_item'],
                'Query': ''' 
                    SELECT DISTINCT Variante.id_variante,
                           Variante.nom_variante
                    FROM Variante
                    JOIN Apparition ON Apparition.variante_id = Variante.id_variante
                    WHERE espece_id = %s; '''
            },

            'Apparitions': {
                'Many': True,
                'Params': ['id_item'],
                'Query': ''' SELECT espece_id, 
                                    variante_id,
                                    carte_id
                             FROM Apparition       
                             WHERE espece_id = %s; '''
            }
        },

        '2': {
            'Main': {
                'Many': False,
                'Params': ['id_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id,
                           
                           Oeuf.id_oeuf,
                           Oeuf.taille_oeuf

                    FROM Nourriture
                    LEFT JOIN Oeuf ON Oeuf.nourriture_id = Nourriture.id_item
                    JOIN Item ON Item.id_item = Nourriture.id_item

                    WHERE Item.id_item = %s
                    AND EXISTS (
                        SELECT 1
                        FROM Compose_Nourriture
                        WHERE Compose_Nourriture.plat_id = Nourriture.id_item
                    );
                '''
            },
            'Ingredient': {
                'Many': True,
                'Params': ['id_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id,
                           Compose_Nourriture.quantite_nourriture

                    FROM Nourriture
                    JOIN Item ON Item.id_item = Nourriture.id_item
                    JOIN Compose_Nourriture ON Compose_Nourriture.ingredient_id = Nourriture.id_item

                    WHERE Compose_Nourriture.plat_id = %s;
                '''
            },
            'Effets': {
                'Many': True,
                'Params': ['id_item'],
                'Query': '''
                    SELECT Effet.id_effet,
                           Effet.libelle_effet

                    FROM Effet
                    JOIN Effet_Nourriture ON Effet_Nourriture.effet_id = Effet.id_effet

                    WHERE Effet_Nourriture.nourriture_id = %s;
                '''
            },

            'Consomme': {
                'Many': True,
                'Params': ['id_item'],
                'Query': ''' SELECT Item.id_item,
                                    Item.nom_item,
                           Item.image_item,
                                    Item.prix_item,
                                    Item.commande_admin_item,
                                    Item.type_item_id
                                    
                             
                             FROM Espece
                             JOIN Item ON Item.id_item = Espece.id_item
                             JOIN Nourriture ON Nourriture.id_item = Espece.nourriture_id
                             
                             WHERE Nourriture.id_item = %s
                             ORDER BY Item.nom_item; '''
            },

            'Pond': {
                'Many': True,
                'Params': ['id_item'],
                'Query': ''' SELECT Item.id_item,
                                    Item.nom_item,
                           Item.image_item,
                                    Item.prix_item,
                                    Item.commande_admin_item,
                                    Item.type_item_id

                             FROM Espece
                             JOIN Item ON Item.id_item = Espece.id_item
                             JOIN Oeuf ON Oeuf.id_oeuf = Espece.oeuf_id
                             JOIN Nourriture ON Nourriture.id_item = Oeuf.nourriture_id
                             
                             WHERE Nourriture.id_item = %s
                             ORDER BY Item.nom_item; '''
            }
        },

        '3': {
            'Main': {
                'Many': False,
                'Params': ['id_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Arme
                    JOIN Item ON Item.id_item = Arme.id_item

                    WHERE Item.id_item = %s;
                '''
            },
            'Munitions': {
                'Many': True,
                'Params': ['id_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Munition
                    JOIN Item ON Item.id_item = Munition.id_item
                    JOIN Arme_Munition ON Arme_Munition.munition_id = Munition.id_item

                    WHERE Arme_Munition.arme_id = %s;
                '''
            },
        },

        '4': {
            'Main': {
                'Many': False,
                'Params': ['id_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Munition
                    JOIN Item ON Item.id_item = Munition.id_item

                    WHERE Item.id_item = %s;
                '''
            },
        },

        '5': {
            'Main': {
                'Many': False,
                'Params': ['id_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Structure
                    JOIN Item ON Item.id_item = Structure.id_item

                    WHERE Item.id_item = %s;
                '''
            },
        },

        '6': {
            'Main': {
                'Many': False,
                'Params': ['id_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Objet
                    JOIN Item ON Item.id_item = Objet.id_item

                    WHERE Item.id_item = %s;
                '''
            },
        },

        '7': {
            'Main': {
                'Many': False,
                'Params': ['id_item'],
                'Query': '''
                    SELECT Item.id_item,
                           Item.nom_item,
                           Item.image_item,
                           Item.prix_item,
                           Item.commande_admin_item,
                           Item.type_item_id

                    FROM Trophe
                    JOIN Item ON Item.id_item = Trophe.id_item

                    WHERE Item.id_item = %s;
                '''
            },
        },
    },


    # ─────────────────────────────────────────────
    #  Requêtes permettant de construire les formulaires d'ajout
    # ─────────────────────────────────────────────

    'add_get': {

        '1': {
            'Nourriture': {
                'Many': True,
                'Params': [],
                'Query': ''' SELECT Item.id_item,
                                    Item.nom_item,
                                    Item.image_item,
                                    Item.prix_item,
                                    Item.commande_admin_item,
                                    Item.type_item_id
        
                             FROM Nourriture
                             JOIN Item ON Item.id_item = Nourriture.id_item
                             
                             ORDER BY Item.nom_item; '''
            },

            'Oeuf': {
                'Many': True,
                'Params': [],
                'Query': ''' SELECT id_oeuf,
                                    taille_oeuf
                             FROM Oeuf; '''
            },

            'Biome': {
                'Many': True,
                'Params': [],
                'Query': ''' SELECT id_biome,
                                    nom_biome
                             FROM Biome; '''
            },

            'Variante': {
                'Many': True,
                'Params': [],
                'Query': ''' SELECT id_variante, 
                                    nom_variante 
                             FROM Variante; '''

            },

            'Carte': {
                'Many': True,
                'Params': [],
                'Query': ''' SELECT id_carte,
                                    nom_carte
                             FROM Carte; '''
            },

            'Trophe': {
                'Many': True,
                'Params': [],
                'Query': ''' SELECT Item.id_item,
                                   Item.nom_item,
                                   Item.image_item,
                                   Item.prix_item,
                                   Item.commande_admin_item,
                                   Item.type_item_id
        
                            FROM Trophe
                            JOIN Item ON Item.id_item = Trophe.id_item; '''
            }
        },

        '2': {
            'Ingredient': {
                'Many': True,
                'Params': [],
                'Query': ''' SELECT Item.id_item,
                                    Item.nom_item,
                                    Item.image_item,
                                    Item.prix_item,
                                    Item.commande_admin_item,
                                    Item.type_item_id
                                            
                             FROM Nourriture
                             JOIN Item ON Item.id_item = Nourriture.id_item; '''
            }
        },

        '3': {
            'Munition': {
                'Many': True,
                'Params': [],
                'Query': ''' SELECT Item.id_item,
                                    Item.nom_item,
                                    Item.image_item,
                                    Item.prix_item,
                                    Item.commande_admin_item,
                                    Item.type_item_id

                             FROM Munition
                             JOIN Item ON Item.id_item = Munition.id_item; '''
            }
        },
        '4': {},
        '5': {},
        '6': {},
        '7': {}
    },


    # -------------------------------------------------------------------------------------------------
    #  Requêtes permettant d'enregistrer les nouvelles infos n'ont pas été mises ici car trop complexes
    # -------------------------------------------------------------------------------------------------
}