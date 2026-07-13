function refreshQuantite(input) {

    let quantite_panier = parseInt(input.value);

    if (!Number.isInteger(quantite_panier)) {
        alert("La saisie ne doit pas comporter d'autres caractères que des chiffres");
        return 1;
    }

    if (quantite_panier < 1) {
        alert("Impossible de passer la quantité de l'item à une valeur inférieure à 1");
        return 1;
    }

    if (quantite_panier > (2**31)-1) {
        alert("Valeur maximale atteinte");
        return 1;
    }

    let form = input.closest("form");
    let id_item         = form.querySelector('[name="id_item"]').value;
    let id_sexe         = form.querySelector('[name="id_sexe"]').value;

    fetch(`/membre/panier/add`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `id_item=${id_item}&quantite_panier=${quantite_panier}&id_sexe=${id_sexe}`
            })

            .then(response => response.text())
            .then(html => {
                document.querySelector("main").innerHTML = html;
            });
}