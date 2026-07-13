function refreshCommandes(id_commande) {

    fetch(`/membre/commandes/details?id_commande=${id_commande}`)
            .then(response => response.text())
            .then(html => {
                document.getElementById("details").innerHTML = html;
            });
}