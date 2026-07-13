function refreshReventes(id_revente) {

    fetch(`/membre/reventes/details?id_revente=${id_revente}`)
            .then(response => response.text())
            .then(html => {
                document.getElementById("details").innerHTML = html;
            });
}