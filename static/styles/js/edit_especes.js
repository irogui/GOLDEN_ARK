document.addEventListener("DOMContentLoaded", function() {

    const variantes = document.querySelectorAll(".variante-checkbox");
    const container = document.getElementById("apparitions");

    const APP_SET = new Set(
        APPARITIONS_EXISTANTES.map(a => `${a.variante_id}-${a.carte_id}`)
    );

    variantes.forEach(v => {
        v.addEventListener("change", refreshTable);
    });

    refreshTable();

    function refreshTable() {
        container.innerHTML = "";

        const variantesCochees = Array.from(variantes).filter(v => v.checked);

        const table = document.createElement("table");
        table.classList.add("apparitions-table");

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

                if (APP_SET.has(`${v.value}-${carte.id_carte}`)) {
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