function refreshCommandes(id_commande) {

    fetch(`/admin/commandes/details?id_commande=${id_commande}`)
            .then(response => response.text())
            .then(html => {
                document.getElementById("details").innerHTML = html;
            });
}

function refreshReventes(id_revente) {

    fetch(`/admin/reventes/details?id_revente=${id_revente}`)
            .then(response => response.text())
            .then(html => {
                document.getElementById("details").innerHTML = html;
            });
}