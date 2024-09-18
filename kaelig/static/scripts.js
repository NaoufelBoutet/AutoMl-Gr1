
function setupDragAndDrop(dragObjectId, dropZoneId,clonage) {
    const dragObject= 0
    const dropZone= 0
    if (clonage===true) {
        dragObject = document.getElementsById(dragObjectId);
        dropZone = document.getElementsByID(dropZoneId);       
    } else {
        dragObject = document.getElementsByClassName(dragObjectId);
        dropZone = document.getElementsById(dropZoneId);  
    }

    // Obtenir les dimensions de la zone de drop
    const positionXzone = dropZone.offsetLeft;
    const positionYzone = dropZone.offsetTop;

    // Gérer le début du drag (dragstart)
    dragObject.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text', e.target.id); // Stocke l'ID de l'élément
        console.log(e.dataTransfer.setData('text', e.target.id))
        if (clonage===true) {
            e.dataTransfer.effectAllowed = 'copy'; // Autorise la copie
        }
        else {
            e.dataTransfer.effectAllowed = 'move';
        }
    });

    // Empêche le comportement par défaut pour permettre le drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault(); // Nécessaire pour autoriser le drop
    });

    // Gérer le drop
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        var listClone = document.getElementsByClassName('clone');
        let nbClone = listClone.length;
        const zoneHeight = parseFloat(window.getComputedStyle(dropZone).getPropertyValue('height'));
        const dragObjectHeight = parseInt(window.getComputedStyle(dragObject).getPropertyValue('height'));
        const dragObjectWidth = parseInt(window.getComputedStyle(dragObject).getPropertyValue('width'));

        // Calculer le décalage
        let adjustX = nbClone * dragObjectHeight;
        let adjustY = dragObjectWidth;
        while (adjustX / zoneHeight > 1) {
            adjustX -= zoneHeight;
            adjustY += dragObjectWidth;
        }

        let positionX = e.clientX;
        let positionY = e.clientY;
        let positionXfinal = positionX - positionXzone;
        let positionYfinal = positionY - positionYzone;

        const id = e.dataTransfer.getData('text'); // Récupère l'ID de l'élément
        const draggedElement = document.getElementById(id);

        if (clonage===true){
            const clone = draggedElement.cloneNode(true);
            clone.classList.add('clone'); // Ajoute une classe au clone (si nécessaire)

            // Positionner le clone
            clone.setAttribute("style", `left:${positionXfinal - (adjustX + dragObjectHeight)}px;top:${positionYfinal - adjustY}px;position:relative`);
            clone.setAttribute('Id',`clone${nbClone}`)
            // Ajoute le clone dans la zone de drop
            dropZone.appendChild(clone);
        }
        else {
            dropZone.appendChild(draggedElement.setAttribute("style", `left:${positionXfinal - (adjustX + dragObjectHeight)}px;top:${positionYfinal - adjustY}px;position:relative`));

            }
    });
}

document.addEventListener('click', (e)=>{
    let  clickedElement = e.target; 
    let elementId = clickedElement.id;
})
// Appel de la fonction avec des paramètres
document.addEventListener('DOMContentLoaded', () => {
    setupDragAndDrop('object_draggable', 'zone_drag',true);
});
