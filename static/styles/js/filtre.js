function reloadItems() {

    let search_item = document.getElementById('search_item').value;
    let id_type_item = document.getElementById('id_type_item').value;

    fetch(`/boutique/items/search?search_item=${search_item}&id_type_item=${id_type_item}`)
            .then(response => response.text())
            .then(html => {
                document.getElementById("select").innerHTML = html;
            });
}