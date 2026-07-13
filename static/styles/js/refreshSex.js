function refreshSex(input, event) {
    event.preventDefault();

    let form = input.closest("form");

    let quantite_panier = parseInt(form.querySelector('[name="quantite_panier"]').value);

    if (!Number.isInteger(quantite_panier)) {
        confirm('Tu serais pas un FDP à mettre autre chose que des chiffres par hasard ?');
        return 1;
    }

    let id_item = form.querySelector('[name="id_item"]').value;
    let id_sexe = form.querySelector('[name="id_sexe"]').value;

    fetch(`/membre/panier/sexe`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `id_item=${id_item}&quantite_panier=${quantite_panier}&id_sexe=${id_sexe}`
            })

            .then(response => response.text())
            .then(html => {
                document.querySelector("main").innerHTML = html;
            });
}