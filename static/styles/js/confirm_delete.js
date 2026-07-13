function confirm_delete(id_item) {
    let message = `ATTENTION \n\nVoulez-vous vraiment supprimer l'item: (id_item: ${id_item}) ? \nCette action est IRRÉVERSIBLE !`;

    if (confirm(message)) {
        window.location.href = '/boutique/items/delete?id_item=' + id_item;
    }
}