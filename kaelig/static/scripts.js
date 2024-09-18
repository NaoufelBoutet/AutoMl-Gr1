document.addEventListener('DOMContentLoaded', () => {
    const drag_object = document.getElementById("object_draggable");
    const zone_drag = document.getElementById('zone_drag');
    const positionXzone=zone_drag.offsetLeft;
    const positionYzone=zone_drag.offsetTop;

    // Gérer le début du drag (dragstart)
    drag_object.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text', e.target.id); // Stocke l'ID de l'élément
        e.dataTransfer.effectAllowed = 'copy'; // Autorise la copie
    });

    // Empêche le comportement par défaut pour permettre le drop
    zone_drag.addEventListener('dragover', (e) => {
        e.preventDefault(); // Nécessaire pour autoriser le drop
    });

    // Gérer le drop
    zone_drag.addEventListener('drop', (e) => {
        e.preventDefault();
        var nb_clone= document.getElementsByClassName('clone')
        let positionX=e.clientX
        let positionY=e.clientY
        let positionXfinal=positionX-positionXzone
        let positionYfinal=positionY-positionYzone
        const id = e.dataTransfer.getData('text'); // Récupère l'ID de l'élément
        const draggedElement = document.getElementById(id);

        // Crée un clone de l'élément déplacé
        const clone = draggedElement.cloneNode(true);
        clone.classList.add('clone'); // Ajoute une classe au clone (si nécessaire)
        clone.setAttribute("style", `left:${positionXfinal}px;top:${positionYfinal}px;position:relative`);

        // Ajoute le clone dans la zone de drop
        zone_drag.appendChild(clone);
    });
});
