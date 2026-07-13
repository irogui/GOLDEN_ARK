function confirmerSuppression(id_espece, nom_espece) {
    let message = 'ATTENTION \n\nVoulez-vous vraiment supprimer cette créature ? \nCette action est IRRÉVERSIBLE !!!';

    if (confirm(message)) {
        window.location.href = '/boutique/especes/delete?id_espece=' + id_espece + '&nom_espece=' + nom_espece;
    }
}