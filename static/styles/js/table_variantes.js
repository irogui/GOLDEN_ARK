document.addEventListener("DOMContentLoaded", function() {
    const variantes = document.querySelectorAll(".radio_variantes");
    const container = document.getElementById("apparitions");

    variantes.forEach(v => {
        v.addEventListener("change", refreshTable);
    });

    refreshTable();

    function refreshTable() {
        container.innerHTML = "";
        const variantesCochees = Array.from(variantes).filter(v => v.checked);

        const table = document.createElement("table");
        table.classList.add("table_3");

        const thead = document.createElement("thead");
        const headerRow = document.createElement("tr");
        const emptyTh = document.createElement("th");
        emptyTh.textContent = "";
        headerRow.appendChild(emptyTh);

        variantesCochees.forEach(v => {
            const th = document.createElement("th");
            th.textContent = v.dataset.nom;
            headerRow.appendChild(th);
        });

        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = document.createElement("tbody");

        CARTES.forEach(carte => {
            const row = document.createElement("tr");
            const tdNom = document.createElement("td");
            tdNom.textContent = carte.nom_carte;
            row.appendChild(tdNom);

            variantesCochees.forEach(v => {
                const td = document.createElement("td");
                const input = document.createElement("input");
                input.type = "checkbox";
                input.name = `apparitions_${v.value}[]`;
                input.value = carte.id_carte;

                const existe = APPARITIONS_EXISTANTES.some(a =>
                    String(a.variante_id) === String(v.value) &&
                    String(a.carte_id) === String(carte.id_carte)
                );
                if (existe) {
                    input.checked = true;
                }

                td.appendChild(input);
                row.appendChild(td);
            });

            tbody.appendChild(row);
        });

        table.appendChild(tbody);
        container.appendChild(table);
    }
});