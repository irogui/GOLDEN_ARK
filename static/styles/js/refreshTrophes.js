function refreshTrophes(input) {

    let quantite_voulue = parseInt(input.value);

    if (!Number.isInteger(quantite_voulue)) {
        confirm("Impossible d'entrer autre chose que des chiffres dans ce champ");
        return 1;
    }

    if (quantite_voulue < 0) {
        confirm("Impossible d'entrer un nombre inférieur à 1 dans ce champ");
        return 1;
    }

    if (quantite_voulue > (2**31)-1) {
        alert("Valeur maximale atteinte du champ atteinte");
        return 1;
    }

    let form = input.closest("form");
    let id_item = form.querySelector('[name="id_item"]').value;
    let prix_item = form.querySelector('[name="prix_item"]').value;
    let total_vente = form.querySelector('[name="total_vente"]').value;


    fetch(`/membre/reventes/add`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `id_item=${id_item}&quantite_voulue=${quantite_voulue}&total_vente=${total_vente}&prix_item=${prix_item}`
            })

            .then(response => response.text())
            .then(html => {
                document.querySelector("main").innerHTML = html;
            });
}